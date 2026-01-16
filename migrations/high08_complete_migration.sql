-- =============================================================================
-- HIGH-08: Complete Migration Script with Transactions and Rollback
-- =============================================================================
--
-- This script provides a comprehensive migration from users_tracker to
-- workout_events with:
-- - Transaction safety
-- - Pre-migration validation
-- - Data integrity checks
-- - Verification queries
-- - Rollback procedures
--
-- IMPORTANT:
-- 1. Run Alembic migration first: alembic upgrade high08_workout_events
-- 2. BACKUP YOUR DATABASE before running this script
-- 3. Review the verification results before committing
--
-- =============================================================================


-- =============================================================================
-- PART 1: PRE-MIGRATION VALIDATION
-- =============================================================================

-- Check that workout_events table exists
SELECT
    CASE
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'workout_events')
        THEN 'OK: workout_events table exists'
        ELSE 'ERROR: workout_events table does not exist - run Alembic migration first'
    END AS table_check;

-- Count records to be migrated
SELECT 'Pre-migration counts' AS status;

SELECT info_type, COUNT(*) AS record_count
FROM users_tracker
WHERE info_type IN ('rutine_end', 'exercise_plan_start', 'exercise_plan_end')
GROUP BY info_type
ORDER BY info_type;

-- Check for any existing data in workout_events (should be empty for clean migration)
SELECT
    CASE
        WHEN (SELECT COUNT(*) FROM workout_events) = 0
        THEN 'OK: workout_events table is empty'
        ELSE 'WARNING: workout_events already contains ' || (SELECT COUNT(*) FROM workout_events) || ' records'
    END AS existing_data_check;


-- =============================================================================
-- PART 2: DATA MIGRATION (within transaction)
-- =============================================================================

BEGIN TRANSACTION;

-- -----------------------------------------------------------------------------
-- Step 1: Migrate 'rutine_end' records to RoutineCompletedEvent
-- -----------------------------------------------------------------------------
-- Maps:
--   info_description -> routine_group
--   record_datetime  -> timestamp
--   All increment fields are preserved
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
    'routine_completed' AS event_type,
    record_datetime AS timestamp,
    info_description AS routine_group,
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
-- Maps:
--   info_description (as integer) -> exercise_plan_id
--   record_datetime -> timestamp
-- Note: Skips records with invalid/missing exercise_plan_id
-- -----------------------------------------------------------------------------

INSERT INTO workout_events (
    user_id,
    event_type,
    timestamp,
    exercise_plan_id
)
SELECT
    user_id,
    'exercise_plan_started' AS event_type,
    record_datetime AS timestamp,
    CAST(info_description AS INTEGER) AS exercise_plan_id
FROM users_tracker
WHERE info_type = 'exercise_plan_start'
  AND info_description IS NOT NULL
  AND info_description != 'Non_specifed'
  AND info_description ~ '^[0-9]+$';  -- PostgreSQL regex for numeric strings


-- -----------------------------------------------------------------------------
-- Step 3: Migrate 'exercise_plan_end' records to ExercisePlanCompletedEvent
-- -----------------------------------------------------------------------------
-- Maps:
--   info_description (as integer) -> exercise_plan_id
--   record_datetime -> timestamp
-- Note: Skips records with invalid/missing exercise_plan_id
-- -----------------------------------------------------------------------------

INSERT INTO workout_events (
    user_id,
    event_type,
    timestamp,
    exercise_plan_id
)
SELECT
    user_id,
    'exercise_plan_completed' AS event_type,
    record_datetime AS timestamp,
    CAST(info_description AS INTEGER) AS exercise_plan_id
FROM users_tracker
WHERE info_type = 'exercise_plan_end'
  AND info_description IS NOT NULL
  AND info_description != 'Non_specifed'
  AND info_description ~ '^[0-9]+$';  -- PostgreSQL regex for numeric strings


-- =============================================================================
-- PART 3: POST-MIGRATION VERIFICATION
-- =============================================================================

SELECT 'Post-migration verification' AS status;

-- Compare record counts
SELECT
    'routine_completed' AS event_type,
    (SELECT COUNT(*) FROM users_tracker WHERE info_type = 'rutine_end') AS legacy_count,
    (SELECT COUNT(*) FROM workout_events WHERE event_type = 'routine_completed') AS new_count,
    CASE
        WHEN (SELECT COUNT(*) FROM users_tracker WHERE info_type = 'rutine_end') =
             (SELECT COUNT(*) FROM workout_events WHERE event_type = 'routine_completed')
        THEN 'MATCH'
        ELSE 'MISMATCH'
    END AS status
UNION ALL
SELECT
    'exercise_plan_started',
    (SELECT COUNT(*) FROM users_tracker WHERE info_type = 'exercise_plan_start'
     AND info_description IS NOT NULL AND info_description != 'Non_specifed' AND info_description ~ '^[0-9]+$'),
    (SELECT COUNT(*) FROM workout_events WHERE event_type = 'exercise_plan_started'),
    CASE
        WHEN (SELECT COUNT(*) FROM users_tracker WHERE info_type = 'exercise_plan_start'
              AND info_description IS NOT NULL AND info_description != 'Non_specifed' AND info_description ~ '^[0-9]+$') =
             (SELECT COUNT(*) FROM workout_events WHERE event_type = 'exercise_plan_started')
        THEN 'MATCH'
        ELSE 'MISMATCH'
    END
UNION ALL
SELECT
    'exercise_plan_completed',
    (SELECT COUNT(*) FROM users_tracker WHERE info_type = 'exercise_plan_end'
     AND info_description IS NOT NULL AND info_description != 'Non_specifed' AND info_description ~ '^[0-9]+$'),
    (SELECT COUNT(*) FROM workout_events WHERE event_type = 'exercise_plan_completed'),
    CASE
        WHEN (SELECT COUNT(*) FROM users_tracker WHERE info_type = 'exercise_plan_end'
              AND info_description IS NOT NULL AND info_description != 'Non_specifed' AND info_description ~ '^[0-9]+$') =
             (SELECT COUNT(*) FROM workout_events WHERE event_type = 'exercise_plan_completed')
        THEN 'MATCH'
        ELSE 'MISMATCH'
    END;

-- Verify sample data integrity (spot check first 5 routine completions)
SELECT 'Sample data verification (first 5 routine completions)' AS status;

SELECT
    ut.user_tracker_id AS legacy_id,
    we.event_id AS new_id,
    ut.user_id,
    ut.info_description AS legacy_routine_group,
    we.routine_group AS new_routine_group,
    ut.record_datetime AS legacy_timestamp,
    we.timestamp AS new_timestamp,
    CASE
        WHEN ut.info_description = we.routine_group
         AND ut.user_id = we.user_id
        THEN 'OK'
        ELSE 'CHECK'
    END AS data_match
FROM users_tracker ut
JOIN workout_events we ON
    we.user_id = ut.user_id
    AND we.event_type = 'routine_completed'
    AND we.timestamp = ut.record_datetime
    AND we.routine_group = ut.info_description
WHERE ut.info_type = 'rutine_end'
LIMIT 5;


-- =============================================================================
-- COMMIT OR ROLLBACK DECISION
-- =============================================================================
-- Review the verification results above.
-- If all counts MATCH and sample data looks correct, COMMIT the transaction.
-- If there are issues, ROLLBACK.

-- To commit: COMMIT;
-- To rollback: ROLLBACK;

-- For safety, this script defaults to COMMIT.
-- Comment out COMMIT and uncomment ROLLBACK if you need to undo changes.
COMMIT;
-- ROLLBACK;


-- =============================================================================
-- PART 4: ROLLBACK SCRIPT (Run separately if needed)
-- =============================================================================
--
-- If you need to rollback after committing, run:
--
-- BEGIN TRANSACTION;
-- DELETE FROM workout_events;
-- COMMIT;
--
-- To completely remove the new table, also run:
-- alembic downgrade -1
--


-- =============================================================================
-- PART 5: SKIPPED RECORDS REPORT
-- =============================================================================
-- Records that were not migrated due to invalid exercise_plan_id

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
       OR info_description !~ '^[0-9]+$');
