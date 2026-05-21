# csv-to-sqlite-agent

Agentic data unification across messy multi-source records — built as a small triathlon-data pipeline, generalizable to any domain where the same entities live across systems that don't talk to each other.

## Why this project exists

Hands-on practice with agentic AI: designing tools, eval methodology, and the agent loop end-to-end.

Data unification is the goal allowing me to learn how to handle messy multi-source input, ambiguous matches, but remain small enough to grade exhaustively. The eval-first methodology (define success before writing the agent) carries over from rubric-design work for LLM-as-judge research at Meta.

## Project status

In-progress portfolio project. Current state:

- Data spec, schema, and ground truth: complete
- Eval methodology and rubric design: complete
- Tools layer: complete (7 tools — `inspect_csv`, `read_csv`, 4 insert paths, `run_query`)
- System prompt: complete
- Agent loop: complete (with live CoT printing and JSONL run logging)
- Eval harness — deterministic layer: complete (16 pytest checks against the golden DB)
- Eval harness — manual rubric layer: planned
- Eval harness — LLM-as-judge layer: planned

Design decisions are documented in the sections below.

## What it does

Given three messy CSVs (IRONMAN race results, USAT membership registry, Strava activity feed) describing partially-overlapping populations of triathletes, the agent unifies them into a normalized SQLite database where each real-world athlete is one row.

Concrete example — **Michael O'Brien (A6)**:

- IRONMAN: `Michael O'Brien`, athlete_id `IM-2014-029445`, raced Texas and Kona 2024
- USAT: last name registered as `o'brien` (lowercase), member `USAT-1011228`
- Strava: username `tridadrunner` **no name overlap with the other two sources**

The agent must recognize all three as the same person (DOB + race date + country + age group cross-reference), normalize the canonical name to `Michael O'Brien`, attach all three source IDs to one unified record, and write a provenance note that flags the lowercase USAT entry and the unusual Strava username for a human reviewer.


## Design decisions

**Eval-first sequence.** Goldens before agent. The 20-athlete population, the truth table, the database schema, and the 13 deterministic checks all exist in `data/SPEC.md` before any agent code is written. The spec is the contract; the agent is graded against it. This means the failure modes are knowable in advance — "did you split the two John Smiths?", "did you exclude Mia Castellanos's fake Texas finish?" — instead of being discovered during ad-hoc inspection of agent output.

**Layered eval methodology.** Two layers, on purpose:

1. **Deterministic checks (13).** Cheap, fast, run on every change. Schema integrity, FK validity, row counts, presence/absence of specific records, exact-match spot checks. Catches structural regressions immediately. These are pass/fail — no rubric needed.
2. **LLM-as-judge rubrics (3 dimensions).** For things determinism can't grade: canonical name quality (is `O'Brien` capitalized correctly?), provenance note quality (does the note explain *and* suggest reviewer action?), Strava activity classification reasoning (was the training ride correctly excluded? was the fake Texas finish flagged?). 1–3 scale with anchor cases drawn from the spec.

The split mirrors what works in production LLM evals: pin everything you can to deterministic checks first, then use judges only for the genuinely fuzzy quality dimensions. The deterministic layer is what makes the judge layer trustworthy — when the judge gives a 3, you already know the structure is right.

**Schema-fixed agent.** The target schema is part of the spec, not something the agent designs. The agent's responsibility is entity resolution and data loading — the *repetitive* part of a migration where consistency and scale matter. Schema design is a one-time human decision that requires domain knowledge about what entities mean and what queries the downstream system needs to support. For a generalized version of this problem (e.g., contractor data migration where target schemas aren't known up front), the natural extension is a schema-proposal step where the agent suggests a schema for human review, then loads against the approved schema. That's deliberately out of scope here — see "future work" below.

**Tool boundary choice.** Seven tools, split between read-only inspection (`inspect_csv`, `read_csv`, `run_query`) and writes (`insert_athlete`, `insert_race`, `insert_race_result`, `insert_source_metadata`). Two design points worth calling out:

- `run_query` enforces a SELECT-only guard at the tool boundary. The agent can use it for verification queries during its loop, but can't issue destructive SQL through it. This is an input guardrail at a tool boundary, in the sense of Huyen ch. 10.
- The split between `inspect_csv` (returns columns + 5-row sample) and `read_csv` (returns all rows) was introduced after Run 1 surfaced a tool design bug — see "Eval results" below. The two-tool pattern lets the agent get a cheap overview first, then commit to loading the full file when it needs to.

**Why this domain.** Triathlon data has the structural property that makes entity resolution genuinely hard: the same athletes appear in three independent systems with different IDs, different formatting conventions, and different completeness profiles. IRONMAN cares about race results, USAT cares about membership and demographics, Strava cares about activity. None of them share a primary key. The mess is real, not synthetic — and it's small enough to grade exhaustively. The same pattern shows up in any domain where the same customers, patients, parts, or assets live across systems that don't talk to each other.

## Eval results

### Run 1 — tool design bug surfaced by the deterministic eval

The first end-to-end agent run produced 7 of 20 athletes, 10 of 26 race results, and 7 of 20 source_metadata rows. All four tables existed with correct schemas, all schemas matched the golden, and foreign key integrity held — but more than half the population was missing.

The deterministic eval caught it on the first run. Specifically:

- `test_athletes_row_count`: 7 ≠ 20
- `test_race_results_row_count`: 10 ≠ 26
- `test_metadata_row_count`: 7 ≠ 20
- `test_john_smith_disambiguation`, `test_mike_foster_unification`, `test_source_metadata_matches_golden`, `test_spot_checks`: all failed on missing-record content checks

The initial hypothesis was that the agent was conservatively skipping hard cases (A6 no-name-match, A8 nickname, A20 fake finish). The trajectory log refuted that: the 13 missing athletes had **contiguous** `unified_id`s (8–20), not scattered. That pattern is "stopped processing" rather than "cherry-picked the easy ones."

Reading the JSONL log surfaced the actual cause: a **tool design bug, not an agent reasoning bug**. The `inspect_csv` tool returned only the first 5 rows per file by design. The agent saw 5 of 26 IRONMAN rows, 5 of 18 USAT rows, 5 of 17 Strava rows, and had no other way to access the remaining data. It tried three workarounds — SQL-querying the CSV directly, searching for a SQLite CSV extension, re-calling `inspect_csv` to see if it paginated — before degrading gracefully: processing the 7 athletes it had visibility into, writing detailed provenance notes flagging what it couldn't see (Sarah Mitchell's unverified Kona claim, Lisa Nakamura's missing DOB, Jennifer Patel's Strava–IRONMAN time match as cross-source confirmation), and running its own integrity checks before declaring done.

The fix was a one-line behavioral change wrapped in a small architectural one: add a `read_csv` tool that returns the full file (vs. `inspect_csv`'s 5-row preview), register it in the agent's tool dispatch, update the system prompt to teach the two-step pattern (`inspect_csv` to understand structure, then `read_csv` before insertion).

**The methodological takeaway.** The eval-first sequence paid off here in a way that ad-hoc inspection wouldn't have. A skim of the agent's output looks competent — every inserted athlete is correct, every cross-source match is correct, every flag note is reasonable. The 7-vs-20 gap only becomes obvious against a known ground truth. The deterministic layer caught the failure; the trajectory log explained it; the fix was small and targeted because the diagnosis was specific.

### Run 2 — *pending*

Re-running against the fixed tools is the next step. Results will be populated here once the agent completes and the eval suite is re-run.



## What I learned

- The eval is where the methodology lives. Designing the deterministic checks against the golden DB before writing the agent meant Run 1's failure was a specific, diagnosable signal ("agent stopped at athlete 7, here are the exact records missing") rather than a vague "output looks off."
- Tool design is part of agent correctness. The agent's behavior in Run 1 was bounded by what its tools made possible. A 5-row preview tool for a task that needs full data access is the kind of bug that doesn't show up in unit tests of the tool — only in end-to-end agent behavior.
- Graceful degradation under tool constraints is itself a positive signal. The Run 1 agent didn't confabulate or fail loudly; it processed what it could verify, flagged what it couldn't, and ran its own integrity checks before stopping. That's the conservative failure mode you want for entity resolution.
- Reading the JSONL trajectory log is non-negotiable for debugging an agent. The `output.db` told me *what* was wrong; only the log explained *why*.

## Future work

- **Manual rubric eval layer.** Dim 1 (canonical name), Dim 2 (provenance notes), Dim 3 (Strava classification reasoning), 1–3 scale, scored by hand against anchor cases in `data/SPEC.md`.
- **LLM-as-judge layer.** Same rubric, automated. The methodological payoff is inter-rater agreement between human and judge scores — that's the number that tells me how much I can trust the judge before scaling to data I can't hand-verify.
- **Schema-flexible variant.** Add a `create_table` tool and let the agent propose its own target schema. Requires a fundamentally different eval — semantic equivalence ("does the agent's schema preserve the same information as mine?") rather than structural string-matching. This is the bootstrapping-eval problem for greenfield agents and would warrant its own project.

## Repo structure

```
csv-to-sqlite-agent/
├── README.md                       — this file
├── requirements.txt                — Python deps (anthropic, pandas, pytest)
├── agent.py                        — agent loop + tool definitions + system prompt
├── tools.py                        — tool implementations (CSV I/O, SQLite inserts, run_query)
├── schema.sql                      — empty-schema initializer for output.db
├── data/
│   ├── SPEC.md                     — data contract: athletes, races, truth table, eval checks, rubric
│   ├── athletes_ironman.csv        — 26 race entries across 5 IRONMAN events
│   ├── athletes_usat.csv           — 18-row USAT registry (A1–A18)
│   └── athletes_strava.csv         — 17 Strava activities including adversarial cases
├── golden/
│   ├── expected_schema.sql         — schema + INSERTs for the golden DB
│   └── expected.db                 — built golden SQLite, 20/5/26/20 row counts
├── output.db                       — agent output (regenerated per run)
├── runs/                           — JSONL trajectory logs from each agent run
└── tests/
    └── test_deterministic.py       — pytest suite, 16 checks (4 row counts, 4 schemas, all-tables, FK integrity, 7 content checks)
```

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Build the golden DB from the spec (one-time)
sqlite3 golden/expected.db < golden/expected_schema.sql

# 4. Initialize an empty output DB
rm -f output.db
sqlite3 output.db < schema.sql

# 5. Run the agent
python agent.py

# 6. Run the deterministic eval against agent output
pytest tests/test_deterministic.py -v
```
