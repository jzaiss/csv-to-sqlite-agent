# Data Spec

This document defines the test data for the agentic CSV-to-SQLite project. It is the source of truth for both the input CSVs and the golden database. The eval harness grades the agent's output against the structures defined here.

## Section 1: Athlete Population

Twenty unique athletes. Each gets a Spec ID (A1-A20) used only in this document; actual data files use system-specific IDs.

| Spec ID | Canonical Name      | DOB        | Country | Notes                                              |
|---------|---------------------|------------|---------|----------------------------------------------------|
| A1      | Sarah Mitchell      | 1987-03-14 | USA     |                                                    |
| A2      | Marcus Chen         | 1990-08-22 | USA     |                                                    |
| A3      | Jennifer Patel      | 1985-11-02 | USA     | 3-race finisher                                    |
| A4      | David Rodriguez     | 1982-06-18 | USA     |                                                    |
| A5      | Emma Thompson       | 1993-01-30 | GBR     | International, one-day USAT license                |
| A6      | Michael O'Brien     | 1979-09-12 | USA     | Adversarial Strava username (no name match)        |
| A7      | Lisa Nakamura       | 1988-04-25 | USA     |                                                    |
| A8      | Michael Foster      | 1991-07-08 | USA     | Nickname variant ("Mike") in USAT and Strava       |
| A9      | Rachel Kim          | 1986-12-19 | USA     |                                                    |
| A10     | Christopher Walsh   | 1984-05-03 | USA     | Not on Strava                                      |
| A11     | Amanda Reyes        | 1992-10-15 | USA     |                                                    |
| A12     | John Smith          | 1983-02-28 | USA     | Adversarial pair with A13                          |
| A13     | John Smith          | 1995-07-19 | CAN     | Adversarial pair with A12 — same name, different person |
| A14     | Priya Krishnan      | 1989-09-06 | USA     | Not on Strava                                      |
| A15     | Thomas Anderson     | 1981-11-23 | USA     | Quoted nickname in Strava display name             |
| A16     | Olivia Bennett      | 1994-03-11 | USA     | USAT-only — annual member who didn't race          |
| A17     | Daniel Park         | 1987-08-04 | USA     | USAT-only — annual member who didn't race          |
| A18     | Nina Volkov         | 1990-12-01 | RUS     | International, one-day USAT license                |
| A19     | Tyler Brennan       | 1996-06-27 | USA     | DNF at Lake Placid; partial Strava data            |
| A20     | Mia Castellanos     | 1985-04-17 | USA     | Strava-only; falsely titled "IM Texas finish" activity |

## Section 2: Races

| Race ID | Race Name                          | Date       | Distance  | Athletes                                          |
|---------|------------------------------------|------------|-----------|---------------------------------------------------|
| R1      | IRONMAN St. George 70.3            | 2024-05-04 | half-iron | A2, A3, A7, A11                                   |
| R2      | IRONMAN Texas                      | 2024-04-27 | full      | A4, A6, A9, A14                                   |
| R3      | IRONMAN Coeur d'Alene              | 2024-06-23 | full      | A3, A8, A11, A15                                  |
| R4      | IRONMAN Lake Placid                | 2024-07-21 | full      | A1, A2, A3, A5, A9, A12, A18, A19 (DNF)           |
| R5      | IRONMAN World Championship Kona    | 2024-10-26 | full      | A1, A4, A6, A10, A13, A15                         |

Total IRONMAN file rows: 26 race entries.

## Section 3: IRONMAN File (athletes_ironman.csv)

Schema: `athlete_id, full_name, age_group, country, bib_number, race_name, race_date, swim_time, bike_time, run_time, finish_time, overall_place`

Format conventions:

- `athlete_id`: stable across races, format `IM-YYYY-NNNNNN`
- `full_name`: "First Last" format, properly capitalized
- `age_group`: gender prefix + 5-year band (e.g. `M30-34`, `F40-44`)
- `country`: 3-letter code (USA, GBR, RUS, CAN)
- `race_date`: ISO `YYYY-MM-DD`
- Times: `HH:MM:SS` strings
- `overall_place`: integer for finishers; `DNF` for non-finishers
- `bib_number`: per-race, not stable across events

Mess in this file:

- A19's row at Lake Placid: `swim_time` populated, all other times empty/null, `overall_place = DNF`
- Otherwise clean

## Section 4: USAT File (athletes_usat.csv)

Schema: `member_number, last_name, first_name, dob, age_group_2024, region, email`

Format conventions:

- `member_number`: `USAT-NNNNNNN` for full members, `USAT-999NNNN` for one-day licenses (A5, A13, A18)
- Names split into separate `first_name` and `last_name` columns
- `dob`: `MM/DD/YYYY` format
- `age_group_2024`: same format as IRONMAN
- `region`: three-letter codes (PAC, MTN, NE, MID, SE, SW, NW, GL)
- `email`: optional, may be empty

Athletes present: A1–A18 (18 rows). A19, A20 NOT present.

Mess in this file:

- A6 last name as `o'brien` (lowercase) — tests capitalization handling
- A8 first name registered as `Mike` (not `Michael`) — tests nickname matching
- A5, A17, A18 have empty email fields
- A12 and A13 (both John Smith) have distinct DOBs, regions, and emails

## Section 5: Strava File (athletes_strava.csv)

Schema: `activity_id, username, display_name, activity_date, activity_name, distance_km, moving_time_seconds, kudos_count`

Format conventions:

- `activity_id`: 10-digit integer
- `username`: lowercase with underscores/dots/numbers
- `display_name`: free-form, may include quirky formatting
- `activity_date`: `MMM DD, YYYY` format (e.g., `Jul 21, 2024`)
- `moving_time_seconds`: integer
- `activity_name`: free text from user
- `kudos_count`: integer

Athletes present: A1, A2, A3, A4, A6, A7, A8, A9, A11, A12, A15, A19, A20 (~17 activity rows; A3 splits into 3 activities, A8 has a training ride)

Adversarial cases:

- A6 username `tridadrunner` — no name match possible from username
- A8 display name `Mike F.` — different from IRONMAN `Michael Foster` and USAT `Mike Foster`
- A15 display name `Thomas "Tom" Anderson` — quoted nickname format
- A20 activity name `IM Texas finish 🏆` — false claim, did not actually race
- A19 swim-only activity at Lake Placid confirming DNF
- A4 activity name `Konna 2024` — typo for Kona
- A8 has a training activity titled `CdA prep ride` — should NOT load as race result

## Section 6: Cross-File Truth Table

| Spec | Canonical Name      | IRONMAN ID         | USAT Member #   | Strava Username        | In Sources       |
|------|---------------------|--------------------|-----------------|------------------------|------------------|
| A1   | Sarah Mitchell      | IM-2018-088421     | USAT-1124883    | sarah_swims_bikes_runs | IM, USAT, Strava |
| A2   | Marcus Chen         | IM-2020-156703     | USAT-1198044    | marcus_chen_tri        | IM, USAT, Strava |
| A3   | Jennifer Patel      | IM-2017-066189     | USAT-1089731    | jenpatel_tri           | IM, USAT, Strava |
| A4   | David Rodriguez     | IM-2015-041288     | USAT-1034556    | drod_kona              | IM, USAT, Strava |
| A5   | Emma Thompson       | IM-2021-178902     | USAT-9990012    | (none)                 | IM, USAT         |
| A6   | Michael O'Brien     | IM-2014-029445     | USAT-1011228    | tridadrunner           | IM, USAT, Strava |
| A7   | Lisa Nakamura       | IM-2019-103312     | USAT-1156889    | lnakamura.tri          | IM, USAT, Strava |
| A8   | Michael Foster      | IM-2022-201144     | USAT-1234501    | mfoster88              | IM, USAT, Strava |
| A9   | Rachel Kim          | IM-2018-091775     | USAT-1118822    | rachelk_runs           | IM, USAT, Strava |
| A10  | Christopher Walsh   | IM-2016-052098     | USAT-1067443    | (none)                 | IM, USAT         |
| A11  | Amanda Reyes        | IM-2021-189203     | USAT-1212077    | amanda.reyes           | IM, USAT, Strava |
| A12  | John Smith (USA)    | IM-2017-077812     | USAT-1098344    | jsmith_endurance       | IM, USAT, Strava |
| A13  | John Smith (CAN)    | IM-2023-220011     | USAT-9990047    | (none)                 | IM, USAT         |
| A14  | Priya Krishnan      | IM-2020-148820     | USAT-1182266    | (none)                 | IM, USAT         |
| A15  | Thomas Anderson     | IM-2014-031007     | USAT-1019988    | tom_anderson_tri       | IM, USAT, Strava |
| A16  | Olivia Bennett      | (none)             | USAT-1259014    | (none)                 | USAT only        |
| A17  | Daniel Park         | (none)             | USAT-1117755    | (none)                 | USAT only        |
| A18  | Nina Volkov         | IM-2022-198556     | USAT-9990089    | (none)                 | IM, USAT         |
| A19  | Tyler Brennan       | IM-2024-230004     | (none)          | tylerbrennan96         | IM (DNF), Strava |
| A20  | Mia Castellanos     | (none)             | (none)          | mia_runs_far           | Strava only      |

## Section 7: Golden Database Structure

Four tables. Use SQLite boolean convention (1/0 integers).

```sql
CREATE TABLE athletes (
    unified_id           INTEGER PRIMARY KEY,
    canonical_name       TEXT NOT NULL,
    dob                  TEXT NOT NULL,
    country              TEXT NOT NULL,
    age_group_2024       TEXT,
    ironman_id           TEXT,
    usat_member_number   TEXT,
    strava_username      TEXT,
    has_official_results INTEGER NOT NULL
);

CREATE TABLE races (
    race_id        INTEGER PRIMARY KEY,
    race_name      TEXT NOT NULL,
    race_date      TEXT NOT NULL,
    distance_type  TEXT NOT NULL
);

CREATE TABLE race_results (
    result_id            INTEGER PRIMARY KEY,
    unified_id           INTEGER NOT NULL,
    race_id              INTEGER NOT NULL,
    bib_number           INTEGER,
    swim_time_seconds    INTEGER,
    bike_time_seconds    INTEGER,
    run_time_seconds     INTEGER,
    finish_time_seconds  INTEGER,
    overall_place        INTEGER,
    status               TEXT NOT NULL,
    source               TEXT NOT NULL,
    FOREIGN KEY (unified_id) REFERENCES athletes(unified_id),
    FOREIGN KEY (race_id) REFERENCES races(race_id)
);

CREATE TABLE source_metadata (
    unified_id            INTEGER PRIMARY KEY,
    in_ironman            INTEGER NOT NULL,
    in_usat               INTEGER NOT NULL,
    in_strava             INTEGER NOT NULL,
    strava_activity_count INTEGER NOT NULL DEFAULT 0,
    notes                 TEXT,
    FOREIGN KEY (unified_id) REFERENCES athletes(unified_id)
);
```

Expected row counts: athletes=20, races=5, race_results=26, source_metadata=20. Tyler Brennan's DNF row has only `swim_time_seconds` populated, all other times NULL, `status='DNF'`. Mia Castellanos appears in athletes but has zero rows in race_results. The two John Smiths must remain separate athletes.

## Section 8: Deterministic Eval Checks (13)

1. All four tables exist
2. Each table has expected columns and types
3. Foreign key integrity (`PRAGMA foreign_key_check`)
4. athletes row count = 20
5. races row count = 5
6. race_results row count = 26
7. John Smith disambiguation: exactly 2 athletes named "John Smith" with DOBs 1983-02-28 and 1995-07-19
8. Mike Foster unification: athlete with `ironman_id='IM-2022-201144'` has `usat_member_number='USAT-1234501'` AND `strava_username='mfoster88'`
9. A20 race result exclusion: Mia Castellanos has 0 rows in race_results
10. A19 DNF preservation: Tyler Brennan has 1 row in race_results with `status='DNF'`, `swim_time_seconds` non-NULL, other times NULL
11. source_metadata flags match Section 6 truth table for all 20 athletes
12. Orphan-only flags correct: A16, A17 USAT-only; A20 Strava-only
13. Spot-checks for A3, A6, A12, A19, A20: canonical name, DOB, country, source IDs match truth table

## Section 9: Rubric Layer

Three dimensions:

**Dim 1 — Canonical Name Quality** (manual grading): 1-3 scale. Anchor cases: A6 apostrophe handling, A8 Michael vs Mike, A15 quoted nickname stripping.

**Dim 2 — Provenance Note Quality** (LLM-as-judge): 1-3 scale. Note must explain situation AND suggest reviewer action for top score. Anchor cases: A19 (DNF), A20 (Strava-only fake race), A12/A13 (John Smith disambiguation).

**Dim 3 — Strava Activity Classification Reasoning** (LLM-as-judge): 1-3 scale. Race activities correctly attributed; training and fake claims excluded. Anchor cases: A1 PR activity, A4 Konna typo, A8 prep ride, A20 fake finish.
