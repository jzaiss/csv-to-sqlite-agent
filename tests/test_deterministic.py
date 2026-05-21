"""
Deterministic evaluation checks for csv-to-sqlite-agent.

Compares the agent's output (output.db) against the hand-built ground truth
(golden/expected.db) on the 13 structural and content checks defined in
data/SPEC.md Section 8.

Each check is a pytest function. Run from the project root with:
    pytest tests/test_deterministic.py -v

A passing run means the agent's output matches the golden DB on every
structural and ground-truth dimension. Reasoning quality (canonical names,
provenance notes, Strava classification) is not graded here — those live
in the rubric layer (test_rubric_manual.py, test_judge.py).
"""

import sqlite3

OUTPUT_DB = "output.db"
EXPECTED_DB = "golden/expected.db"

#Helper function to open databases for comparison
def count_rows(db_path, table):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    result = cursor.fetchone()[0]
    conn.close()
    return result

#helper to retrieve DB table names
def get_table_names(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table'")
    result = cursor.fetchall()
    result_set = {row[0] for row in result}
    conn.close()
    return result_set

#helper to retrieve column schemas for a given table
def get_table_schema(db_path, table):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    result = cursor.fetchall()
    schema = {row[1]: (row[2], row[3], row[5]) for row in result}
    conn.close()
    return schema

#helper to check foreign key integrity
def get_fk_violations(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")  # FKs are OFF by default in SQLite
    cursor.execute("PRAGMA foreign_key_check")
    result = cursor.fetchall()
    conn.close()
    return result

#helper to fetch rows matching a WHERE clause, as a list of dicts keyed by column name
def fetch_rows(db_path, table, where_clause="", params=()):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # rows come back as dict-like objects
    cursor = conn.cursor()
    query = f"SELECT * FROM {table}"
    if where_clause:
        query += f" WHERE {where_clause}"
    cursor.execute(query, params)
    result = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return result

#########################################################################################
#Check that the number of athletes in output is correct
def test_athletes_row_count():
   
    assert  count_rows(OUTPUT_DB, "athletes") == count_rows(EXPECTED_DB, "athletes")

def test_athletes_schema():
    assert get_table_schema(OUTPUT_DB, "athletes") == get_table_schema(EXPECTED_DB, "athletes")

#Check that the number of races in output is correct
def test_races_row_count():
   
    assert  count_rows(OUTPUT_DB, "races") == count_rows(EXPECTED_DB, "races")

def test_races_schema():
    assert get_table_schema(OUTPUT_DB, "races") == get_table_schema(EXPECTED_DB, "races")


#Check that the number of races results in output is correct
def test_race_results_row_count():
   
    assert  count_rows(OUTPUT_DB, "race_results") == count_rows(EXPECTED_DB, "race_results")

def test_race_results_schema():
    assert get_table_schema(OUTPUT_DB, "race_results") == get_table_schema(EXPECTED_DB, "race_results")


#Check that the number of source metadata in output is correct
def test_metadata_row_count():
   
    assert  count_rows(OUTPUT_DB, "source_metadata") == count_rows(EXPECTED_DB, "source_metadata")

def test_source_metadata_schema():
    assert get_table_schema(OUTPUT_DB, "source_metadata") == get_table_schema(EXPECTED_DB, "source_metadata")


def test_all_tables_exist():
    expected = get_table_names(EXPECTED_DB)   # the four names, as a set
    output = get_table_names(OUTPUT_DB)    # query output.db, get names back as a set
    
    missing = expected - output
    extra = output - expected
    
    assert output == expected, f"Missing: {missing}, Extra: {extra}"

def test_foreign_key_integrity():
    violations = get_fk_violations(OUTPUT_DB)
    assert violations == [], f"Foreign key violations in output: {violations}"

def test_john_smith_disambiguation():
    smiths = fetch_rows(OUTPUT_DB, "athletes", "canonical_name = ?", ("John Smith",))
    assert len(smiths) == 2, f"Expected 2 John Smiths, found {len(smiths)}"
    dobs = sorted(s["dob"] for s in smiths)
    assert dobs == ["1983-02-28", "1995-07-19"], f"Wrong DOBs for John Smiths: {dobs}"

def test_mike_foster_unification():
    rows = fetch_rows(OUTPUT_DB, "athletes", "ironman_id = ?", ("IM-2022-201144",))
    assert len(rows) == 1, f"Expected 1 athlete with that ironman_id, found {len(rows)}"
    foster = rows[0]
    assert foster["usat_member_number"] == "USAT-1234501", f"USAT id wrong: {foster['usat_member_number']}"
    assert foster["strava_username"] == "mfoster88", f"Strava username wrong: {foster['strava_username']}"

def test_mia_castellanos_no_races():
    mia_rows = fetch_rows(OUTPUT_DB, "athletes", "canonical_name = ?", ("Mia Castellanos",))
    if len(mia_rows) == 0:
        # Mia isn't in athletes at all — depending on your spec, this might be a separate failure
        # but for check #9 specifically, no athlete row → no race results → check passes trivially
        return
    mia_id = mia_rows[0]["unified_id"]
    race_results = fetch_rows(OUTPUT_DB, "race_results", "unified_id = ?", (mia_id,))
    assert race_results == [], f"Mia should have 0 race results, found {len(race_results)}"

def test_tyler_brennan_dnf():
    tyler_rows = fetch_rows(OUTPUT_DB, "athletes", "canonical_name = ?", ("Tyler Brennan",))
    if len(tyler_rows) == 0:
        return  # see note in check #9
    tyler_id = tyler_rows[0]["unified_id"]
    results = fetch_rows(OUTPUT_DB, "race_results", "unified_id = ?", (tyler_id,))
    assert len(results) == 1, f"Tyler should have 1 race result, found {len(results)}"
    dnf = results[0]
    assert dnf["status"] == "DNF", f"Status should be DNF, got {dnf['status']}"
    assert dnf["swim_time_seconds"] is not None, "swim_time_seconds should not be NULL"
    assert dnf["bike_time_seconds"] is None, f"bike_time_seconds should be NULL, got {dnf['bike_time_seconds']}"
    assert dnf["run_time_seconds"] is None, f"run_time_seconds should be NULL, got {dnf['run_time_seconds']}"


def test_source_metadata_matches_golden():
    output_rows = fetch_rows(OUTPUT_DB, "source_metadata")
    expected_rows = fetch_rows(EXPECTED_DB, "source_metadata")
    
    # Index both by unified_id for diffing
    output_by_id = {r["unified_id"]: r for r in output_rows}
    expected_by_id = {r["unified_id"]: r for r in expected_rows}
    
    missing = set(expected_by_id.keys()) - set(output_by_id.keys())
    extra = set(output_by_id.keys()) - set(expected_by_id.keys())
    
    # For ids present in both, check the rows are identical
    differences = []
    for uid in set(expected_by_id) & set(output_by_id):
        if output_by_id[uid] != expected_by_id[uid]:
            differences.append((uid, output_by_id[uid], expected_by_id[uid]))
    
    assert not missing and not extra and not differences, (
        f"Missing unified_ids: {missing}, "
        f"Extra unified_ids: {extra}, "
        f"Differences: {differences}"
    )


def test_orphan_flags():
    # A16 and A17: USAT-only (no ironman_id, no strava_username, only usat_member_number)
    # A20: Strava-only (no ironman_id, no usat_member_number, only strava_username)
    
    expected_orphans = fetch_rows(
        EXPECTED_DB, "athletes",
        "ironman_id IS NULL AND (usat_member_number IS NULL OR strava_username IS NULL)"
    )
    
    for expected in expected_orphans:
        output_match = fetch_rows(
            OUTPUT_DB, "athletes",
            "canonical_name = ?", (expected["canonical_name"],)
        )
        if not output_match:
            continue  # agent skipped this athlete entirely; covered elsewhere
        actual = output_match[0]
        assert actual["ironman_id"] == expected["ironman_id"], \
            f"{expected['canonical_name']}: ironman_id mismatch"
        assert actual["usat_member_number"] == expected["usat_member_number"], \
            f"{expected['canonical_name']}: usat mismatch"
        assert actual["strava_username"] == expected["strava_username"], \
            f"{expected['canonical_name']}: strava mismatch"


def test_spot_checks():
    # The five athletes the SPEC calls out for full-row spot-checking
    spot_check_names = ["Jen Patel", "Michael O'Brien", "John Smith", "Tyler Brennan", "Mia Castellanos"]
    # NOTE: there are two John Smiths — A12 is the one born 1983-02-28
    
    failures = []
    for name in spot_check_names:
        expected = fetch_rows(EXPECTED_DB, "athletes", "canonical_name = ?", (name,))
        output = fetch_rows(OUTPUT_DB, "athletes", "canonical_name = ?", (name,))
        
        if not output:
            failures.append(f"{name}: missing from output")
            continue
        if len(expected) != len(output):
            failures.append(f"{name}: count mismatch (expected {len(expected)}, got {len(output)})")
            continue
        # Compare full rows (sorted by dob to handle the two John Smiths)
        expected_sorted = sorted(expected, key=lambda r: r["dob"])
        output_sorted = sorted(output, key=lambda r: r["dob"])
        for e, o in zip(expected_sorted, output_sorted):
            if dict(e) != dict(o):
                failures.append(f"{name} (dob={e['dob']}): row mismatch — expected {dict(e)}, got {dict(o)}")
    
    assert not failures, "\n".join(failures)





