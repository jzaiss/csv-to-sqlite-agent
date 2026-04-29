PRAGMA foreign_keys = ON;

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

-- athletes
INSERT INTO athletes VALUES (1, 'Sarah Mitchell', '1987-03-14', 'USA', 'F35-39', 'IM-2018-088421', 'USAT-1124883', 'sarah_swims_bikes_runs', 1);
INSERT INTO athletes VALUES (2, 'Marcus Chen', '1990-08-22', 'USA', 'M30-34', 'IM-2020-156703', 'USAT-1198044', 'marcus_chen_tri', 1);
INSERT INTO athletes VALUES (3, 'Jennifer Patel', '1985-11-02', 'USA', 'F35-39', 'IM-2017-066189', 'USAT-1089731', 'jenpatel_tri', 1);
INSERT INTO athletes VALUES (4, 'David Rodriguez', '1982-06-18', 'USA', 'M40-44', 'IM-2015-041288', 'USAT-1034556', 'drod_kona', 1);
INSERT INTO athletes VALUES (5, 'Emma Thompson', '1993-01-30', 'GBR', 'F30-34', 'IM-2021-178902', 'USAT-9990012', NULL, 1);
INSERT INTO athletes VALUES (6, 'Michael O''Brien', '1979-09-12', 'USA', 'M45-49', 'IM-2014-029445', 'USAT-1011228', 'tridadrunner', 1);
INSERT INTO athletes VALUES (7, 'Lisa Nakamura', '1988-04-25', 'USA', 'F35-39', 'IM-2019-103312', 'USAT-1156889', 'lnakamura.tri', 1);
INSERT INTO athletes VALUES (8, 'Michael Foster', '1991-07-08', 'USA', 'M30-34', 'IM-2022-201144', 'USAT-1234501', 'mfoster88', 1);
INSERT INTO athletes VALUES (9, 'Rachel Kim', '1986-12-19', 'USA', 'F35-39', 'IM-2018-091775', 'USAT-1118822', 'rachelk_runs', 1);
INSERT INTO athletes VALUES (10, 'Christopher Walsh', '1984-05-03', 'USA', 'M40-44', 'IM-2016-052098', 'USAT-1067443', NULL, 1);
INSERT INTO athletes VALUES (11, 'Amanda Reyes', '1992-10-15', 'USA', 'F30-34', 'IM-2021-189203', 'USAT-1212077', 'amanda.reyes', 1);
INSERT INTO athletes VALUES (12, 'John Smith', '1983-02-28', 'USA', 'M40-44', 'IM-2017-077812', 'USAT-1098344', 'jsmith_endurance', 1);
INSERT INTO athletes VALUES (13, 'John Smith', '1995-07-19', 'CAN', 'M25-29', 'IM-2023-220011', 'USAT-9990047', NULL, 1);
INSERT INTO athletes VALUES (14, 'Priya Krishnan', '1989-09-06', 'USA', 'F35-39', 'IM-2020-148820', 'USAT-1182266', NULL, 1);
INSERT INTO athletes VALUES (15, 'Thomas Anderson', '1981-11-23', 'USA', 'M40-44', 'IM-2014-031007', 'USAT-1019988', 'tom_anderson_tri', 1);
INSERT INTO athletes VALUES (16, 'Olivia Bennett', '1994-03-11', 'USA', 'F30-34', NULL, 'USAT-1259014', NULL, 0);
INSERT INTO athletes VALUES (17, 'Daniel Park', '1987-08-04', 'USA', 'M35-39', NULL, 'USAT-1117755', NULL, 0);
INSERT INTO athletes VALUES (18, 'Nina Volkov', '1990-12-01', 'RUS', 'F30-34', 'IM-2022-198556', 'USAT-9990089', NULL, 1);
INSERT INTO athletes VALUES (19, 'Tyler Brennan', '1996-06-27', 'USA', 'M25-29', 'IM-2024-230004', NULL, 'tylerbrennan96', 1);
INSERT INTO athletes VALUES (20, 'Mia Castellanos', '1985-04-17', 'USA', 'F35-39', NULL, NULL, 'mia_runs_far', 0);

-- races
INSERT INTO races VALUES (1, 'IRONMAN St. George 70.3', '2024-05-04', 'half-iron');
INSERT INTO races VALUES (2, 'IRONMAN Texas', '2024-04-27', 'full');
INSERT INTO races VALUES (3, 'IRONMAN Coeur d''Alene', '2024-06-23', 'full');
INSERT INTO races VALUES (4, 'IRONMAN Lake Placid', '2024-07-21', 'full');
INSERT INTO races VALUES (5, 'IRONMAN World Championship Kona', '2024-10-26', 'full');

-- race_results
INSERT INTO race_results VALUES (1, 2, 1, 142, 1938, 10125, 6150, 18491, 47, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (2, 3, 1, 358, 2322, 11118, 6922, 20788, 89, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (3, 7, 1, 412, 2150, 10353, 6495, 19244, 71, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (4, 11, 1, 287, 2005, 9952, 5920, 18078, 62, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (5, 4, 2, 521, 3734, 18513, 13338, 35922, 124, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (6, 6, 2, 678, 4135, 19931, 14568, 39093, 287, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (7, 9, 2, 432, 4282, 20895, 15520, 41148, 412, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (8, 14, 2, 589, 4508, 21342, 16113, 42491, 487, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (9, 3, 3, 245, 4335, 21158, 15911, 41908, 398, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (10, 8, 3, 312, 3642, 18138, 13135, 35297, 89, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (11, 11, 3, 388, 4113, 20322, 14895, 39738, 245, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (12, 15, 3, 411, 3918, 19122, 14133, 37735, 156, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (13, 1, 4, 156, 4122, 20538, 14913, 40135, 312, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (14, 2, 4, 89, 3735, 19122, 13698, 37113, 145, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (15, 3, 4, 421, 4462, 21513, 16338, 42942, 425, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (16, 5, 4, 588, 4195, 20891, 15342, 40938, 378, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (17, 9, 4, 244, 4388, 21138, 15775, 41922, 412, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (18, 12, 4, 367, 3942, 19931, 14313, 38898, 232, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (19, 18, 4, 612, 4278, 21342, 15911, 42175, 445, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (20, 19, 4, 488, 3993, NULL, NULL, NULL, NULL, 'DNF', 'ironman');
INSERT INTO race_results VALUES (21, 1, 5, 1142, 3918, 19962, 14118, 38553, 218, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (22, 4, 5, 1287, 3522, 17718, 12731, 34375, 87, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (23, 6, 5, 1455, 3993, 19735, 14322, 38538, 245, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (24, 10, 5, 1189, 3738, 19122, 13735, 37122, 178, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (25, 13, 5, 1622, 3333, 17291, 12342, 33535, 65, 'FINISHED', 'ironman');
INSERT INTO race_results VALUES (26, 15, 5, 1377, 3715, 18738, 13353, 36318, 142, 'FINISHED', 'ironman');

-- source_metadata
INSERT INTO source_metadata VALUES (1, 1, 1, 1, 2, NULL);
INSERT INTO source_metadata VALUES (2, 1, 1, 1, 1, NULL);
INSERT INTO source_metadata VALUES (3, 1, 1, 1, 3, 'Strava activity logged for each of 3 IRONMAN races (St. George, CdA, Lake Placid).');
INSERT INTO source_metadata VALUES (4, 1, 1, 1, 1, 'Strava activity ''Konna 2024'' contains typo for Kona; correctly attributed to IRONMAN World Championship Kona.');
INSERT INTO source_metadata VALUES (5, 1, 1, 0, 0, 'International athlete (GBR) with USAT one-day license.');
INSERT INTO source_metadata VALUES (6, 1, 1, 1, 1, 'USAT last name registered lowercase (''o''brien''); normalized to ''O''Brien''. Strava username ''tridadrunner'' has no name match; resolved via DOB and IRONMAN race date cross-reference.');
INSERT INTO source_metadata VALUES (7, 1, 1, 1, 1, NULL);
INSERT INTO source_metadata VALUES (8, 1, 1, 1, 2, 'USAT and Strava use ''Mike'' nickname; canonicalized to ''Michael'' from IRONMAN registration. Strava ''CdA prep ride'' classified as training and excluded from race_results.');
INSERT INTO source_metadata VALUES (9, 1, 1, 1, 1, NULL);
INSERT INTO source_metadata VALUES (10, 1, 1, 0, 0, NULL);
INSERT INTO source_metadata VALUES (11, 1, 1, 1, 1, NULL);
INSERT INTO source_metadata VALUES (12, 1, 1, 1, 1, 'Two distinct athletes named John Smith in dataset; disambiguated by DOB (1983-02-28) and country (USA).');
INSERT INTO source_metadata VALUES (13, 1, 1, 0, 0, 'Two distinct athletes named John Smith in dataset; disambiguated by DOB (1995-07-19) and country (CAN). USAT one-day license.');
INSERT INTO source_metadata VALUES (14, 1, 1, 0, 0, NULL);
INSERT INTO source_metadata VALUES (15, 1, 1, 1, 1, 'Strava display name ''Thomas "Tom" Anderson'' contains quoted nickname; stripped to canonical name.');
INSERT INTO source_metadata VALUES (16, 0, 1, 0, 0, 'USAT annual member; no race participation in 2024.');
INSERT INTO source_metadata VALUES (17, 0, 1, 0, 0, 'USAT annual member; no race participation in 2024.');
INSERT INTO source_metadata VALUES (18, 1, 1, 0, 0, 'International athlete (RUS) with USAT one-day license.');
INSERT INTO source_metadata VALUES (19, 1, 0, 1, 1, 'DNF at IRONMAN Lake Placid (swim completed, bike not started). Not in USAT roster — possibly raced under one-day license that wasn''t captured. Strava swim activity confirms DNF. Manual review recommended.');
INSERT INTO source_metadata VALUES (20, 0, 0, 1, 1, 'Strava activity ''IM Texas finish 🏆'' claims an IRONMAN Texas finish, but athlete is not in IRONMAN registration. Likely false claim — excluded from race_results. Reviewer should verify.');
