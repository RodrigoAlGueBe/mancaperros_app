-- =============================================================================
-- HIGH-08: SQLite Migration Script
-- =============================================================================
--
-- SQLite-compatible version of the data migration from users_tracker to
-- workout_events table.
--
-- NOTE: SQLite has limited transaction support for DDL, but data migrations
-- within transactions work correctly.
--
-- IMPORTANT:
-- 1. Run Alembic migration first: alembic upgrade high08_workout_events
-- 2. BACKUP YOUR DATABASE before running this script
-- 3. Review the verification results
--
-- =============================================================================


-- =============================================================================
-- PART 1: PRE-MIGRATION COUNTS
-- =============================================================================

-- Count records to be migrated
SELECT 'Pre-migration counts' AS status;

SELECT 'rutine_end' AS info_type, COUNT(*) AS count
FROM users_tracker WHERE info_type = 'rutine_end'
UNION ALL
SELECT 'exercise_plan_start', COUNT(*)
FROM users_tracker WHERE info_type = 'exercise_plan_start'
UNION ALL
SELECT 'exercise_plan_end', COUNT(*)
FROM users_tracker WHERE info_type = 'exercise_plan_end';

-- Check existing records in workout_events
SELECT 'workout_events existing count' AS status, COUNT(*) AS count FROM workout_events;


-- =============================================================================
-- PART 2: DATA MIGRATION
-- =============================================================================

-- Begin transaction for data integrity
BEGIN TRANSACTION;

-- -----------------------------------------------------------------------------
-- Step 1: Migrate 'rutine_end' records to RoutineCompletedEvent
-- -----------------------------------------------------------------------------

INSERT INTO workout_events (
    user_id,
    event_type,
    timestamp,
    routine_group,
    exercise_increments,
    push_increment,
    pull_increment,
    isometric_increment,
    push_time_increment,
    pull_time_increment,
    isometric_time_increment
)
SELECT
    user_id,
    'routine_completed',
    record_datetime,
    info_description,
    exercise_increments,
    COALESCE(push_increment, 0),
    COALESCE(pull_increment, 0),
    COALESCE(isometric_increment, 0),
    COALESCE(push_time_increment, 0),
    COALESCE(pull_time_increment, 0),
    COALESCE(isometric_time_increment, 0)
FROM users_tracker
WHERE info_type = 'rutine_end';


-- -----------------------------------------------------------------------------
-- Step 2: Migrate 'exercise_plan_start' records to ExercisePlanStartedEvent
-- -----------------------------------------------------------------------------
-- Note: SQLite CAST works differently, using typeof() to filter numeric strings

INSERT INTO workout_events (
    user_id,
    event_type,
    timestamp,
    exercise_plan_id
)
SELECT
    user_id,
    'exercise_plan_started',
    record_datetime,
    CAST(info_description AS INTEGER)
FROM users_tracker
WHERE info_type = 'exercise_plan_start'
  AND info_description IS NOT NULL
  AND info_description != 'Non_specifed'
  AND info_description GLOB '[0-9]*';  -- SQLite pattern for numeric strings


-- -----------------------------------------------------------------------------
-- Step 3: Migrate 'exercise_plan_end' records to ExercisePlanCompletedEvent
-- -----------------------------------------------------------------------------

INSERT INTO workout_events (
    user_id,
    event_type,
    timestamp,
    exercise_plan_id
)
SELECT
    user_id,
    'exercise_plan_completed',
    record_datetime,
    CAST(info_description AS INTEGER)
FROM users_tracker
WHERE info_type = 'exercise_plan_end'
  AND info_description IS NOT NULL
  AND info_description != 'Non_specifed'
  AND info_description GLOB '[0-9]*';  -- SQLite pattern for numeric strings


-- Commit the transaction
COMMIT;


-- =============================================================================
-- PART 3: POST-MIGRATION VERIFICATION
-- =============================================================================

SELECT 'Post-migration verification' AS status;

-- Compare routine completion counts
SELECT
    'routine_completed' AS event_type,
    (SELECT COUNT(*) FROM users_tracker WHERE info_type = 'rutine_end') AS legacy_count,
    (SELECT COUNT(*) FROM workout_events WHERE event_type = 'routine_completed') AS new_count;

-- Compare exercise plan start counts
SELECT
    'exercise_plan_started' AS event_type,
    (SELECT COUNT(*) FROM users_tracker WHERE info_type = 'exercise_plan_start'
     AND info_description IS NOT NULL AND info_description != 'Non_specifed'
     AND info_description GLOB '[0-9]*') AS legacy_count,
    (SELECT COUNT(*) FROM workout_events WHERE event_type = 'exercise_plan_started') AS new_count;

-- Compare exercise plan end counts
SELECT
    'exercise_plan_completed' AS event_type,
    (SELECT COUNT(*) FROM users_tracker WHERE info_type = 'exercise_plan_end'
     AND info_description IS NOT NULL AND info_description != 'Non_specifed'
     AND info_description GLOB '[0-9]*') AS legacy_count,
    (SELECT COUNT(*) FROM workout_events WHERE event_type = 'exercise_plan_completed') AS new_count;

-- Total records migrated
SELECT 'Total records in workout_events' AS status, COUNT(*) AS count FROM workout_events;


-- =============================================================================
-- ROLLBACK SCRIPT (Run separately if needed)
-- =============================================================================
--
-- To rollback the data migration:
-- DELETE FROM workout_events;
--
-- To completely remove the table, also run:
-- alembic downgrade -1
--


-- =============================================================================
-- SKIPPED RECORDS REPORT
-- =============================================================================

SELECT 'Records skipped due to invalid exercise_plan_id' AS status;

SELECT
    user_tracker_id,
    user_id,
    info_type,
    info_description,
    record_datetime
FROM users_tracker
WHERE info_type IN ('exercise_plan_start', 'exercise_plan_end')
  AND (info_description IS NULL
       OR info_description = 'Non_specifed'
       OR info_description NOT GLOB '[0-9]*');
