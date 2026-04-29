import csv
import sqlite3

def inspect_csv(filepath):
    n = 5
    row_count = 0
    rows=[]
    with open(filepath, mode='r') as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader):
            if i < n:
                rows.append(row)
            row_count = row_count + 1
    
    return  {
        "columns": reader.fieldnames,
        "row_count": row_count,
        "sample_rows": rows
    }


def insert_athlete(canonical_name, dob, country, age_group_2024,
                   ironman_id, usat_member_number, strava_username,
                   has_official_results):
    
    conn = sqlite3.connect("../output.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO athletes (
            canonical_name, dob, country, age_group_2024,
            ironman_id, usat_member_number, strava_username,
            has_official_results
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (canonical_name, dob, country, age_group_2024,
         ironman_id, usat_member_number, strava_username,
         has_official_results)
    )
    
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    return new_id



def insert_race_result(unified_id, race_id, bib_number,
                       swim_time_seconds, bike_time_seconds, run_time_seconds,
                       finish_time_seconds, overall_place, status, source):
    
    conn = sqlite3.connect("../output.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO race_results (unified_id, race_id, bib_number,
                       swim_time_seconds, bike_time_seconds, run_time_seconds,
                       finish_time_seconds, overall_place, status, source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (unified_id, race_id, bib_number,
                       swim_time_seconds, bike_time_seconds, run_time_seconds,
                       finish_time_seconds, overall_place, status, source
                       )
    )
    
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    return new_id




def insert_race(race_name, race_date, distance_type):
    
    conn = sqlite3.connect("../output.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO races (race_name, race_date, distance_type
        ) VALUES (?, ?, ?)
        """,
        (race_name, race_date, distance_type
            )
    )
    
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    return new_id


def insert_source_metadata(unified_id, in_ironman, in_usat,
                           in_strava, strava_activity_count, notes):
    
    conn = sqlite3.connect("../output.db")
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO source_metadata (unified_id, in_ironman, in_usat,
                           in_strava, strava_activity_count, notes
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (unified_id, in_ironman, in_usat, 
         in_strava, strava_activity_count, notes
            )
    )
    
    conn.commit()
    conn.close()


def run_query(sql):
    if not sql.strip().upper().startswith("SELECT"):
        raise ValueError("run_query only accepts SELECT statements")

    conn = sqlite3.connect("../output.db")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

    


