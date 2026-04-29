# csv-to-sqlite-agent

Agentic data unification across messy multi-source records — built as a small triathlon-data pipeline, generalizable to any domain where the same entities live across systems that don't talk to each other.

## Why this project exists

## Why this project exists

## Why this project exists

Hands-on practice with agentic AI: designing tools, eval methodology, and the agent loop end-to-end.

Data unification is the goal allowing me to learn how to handle messy multi-source input, ambiguous matches, but remain small enough to grade exhaustively. The eval-first methodology (define success before writing the agent) carries over from rubric-design work for LLM-as-judge research at Meta.

## Project status

This is an in-progress portfolio project. Current state:

- Data spec, schema, and ground truth: complete
- Eval methodology and rubric design: complete
- Tools layer: complete (7 tools, all 4 insert paths plus inspect/query)
- System prompt: in progress
- Agent loop: in progress
- Eval harness: planned

Design decisions are documented in the sections below. Code that's still in progress is clearly marked.

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

**Tool boundary choice.** *Placeholder — to be filled in after the agent build.* 


**Why this domain.** Triathlon data has the structural property that makes entity resolution genuinely hard: the same athletes appear in three independent systems with different IDs, different formatting conventions, and different completeness profiles. IRONMAN cares about race results, USAT cares about membership and demographics, Strava cares about activity. None of them share a primary key. The mess is real, not synthetic — and it's small enough to grade exhaustively. The same pattern shows up in any domain where the same customers, patients, parts, or assets live across systems that don't talk to each other.

## Eval results

*Placeholder — populated after agent build.*



## What I learned


## Repo structure

```
csv-to-sqlite-agent/
├── README.md                       — this file
├── requirements.txt                — Python deps (anthropic, pandas, pytest)
├── data/
│   ├── SPEC.md                     — data contract: athletes, races, truth table, eval checks, rubric
│   ├── athletes_ironman.csv        — 26 race entries across 5 IRONMAN events
│   ├── athletes_usat.csv           — 18-row USAT registry (A1–A18)
│   └── athletes_strava.csv         — 17 Strava activities including adversarial cases
├── golden/
│   ├── expected_schema.sql         — schema + INSERTs for the golden DB
│   └── expected.db                 — built golden SQLite, 20/5/26/20 row counts
├── src/                            — agent implementation (TBD)
└── tests/                          — eval harness: deterministic checks + judge rubrics (TBD)
```

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# 3. (Optional) Rebuild the golden DB from the SQL
sqlite3 golden/expected.db < golden/expected_schema.sql

# 4. Run the agent (once src/ is implemented)
python -m src.agent --input data/ --output build/output.db

# 5. Run the eval harness against agent output (once tests/ is implemented)
pytest tests/
```
