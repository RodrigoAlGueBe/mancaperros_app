-- =============================================================================
-- HIGH-08: Migrate data from users_tracker to workout_events
-- =============================================================================
--
-- This script migrates existing data from the legacy users_tracker table
-- to the new workout_events table with proper polymorphic event types.
--
-- IMPORTANT: Run this AFTER creating the workout_events table via Alembic.
--
-- Execution order:
-- 1. Run Alembic migration: alembic upgrade high08_workout_events
-- 2. Run this SQL script to migrate existing data
-- 3. Verify data integrity
-- 4. (Optional) Enable dual-write mode for new events
--
-- =============================================================================

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
    -- info_description contains the exercise_plan_id as string
    CAST(info_description AS INTEGER) AS exercise_plan_id
FROM users_tracker
WHERE info_type = 'exercise_plan_start'
  AND info_description IS NOT NULL
  AND info_description != 'Non_specifed';


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
    'exercise_plan_completed' AS event_type,
    record_datetime AS timestamp,
    -- info_description contains the exercise_plan_id as string
    CAST(info_description AS INTEGER) AS exercise_plan_id
FROM users_tracker
WHERE info_type = 'exercise_plan_end'
  AND info_description IS NOT NULL
  AND info_description != 'Non_specifed';


-- =============================================================================
-- Verification Queries
-- =============================================================================

-- Verify record counts match
-- Run these queries to ensure migration was successful:

-- SELECT 'Legacy routine_end count' AS description, COUNT(*) AS count
-- FROM users_tracker WHERE info_type = 'rutine_end'
-- UNION ALL
-- SELECT 'New routine_completed count', COUNT(*)
-- FROM workout_events WHERE event_type = 'routine_completed'
-- UNION ALL
-- SELECT 'Legacy exercise_plan_start count', COUNT(*)
-- FROM users_tracker WHERE info_type = 'exercise_plan_start'
-- UNION ALL
-- SELECT 'New exercise_plan_started count', COUNT(*)
-- FROM workout_events WHERE event_type = 'exercise_plan_started'
-- UNION ALL
-- SELECT 'Legacy exercise_plan_end count', COUNT(*)
-- FROM users_tracker WHERE info_type = 'exercise_plan_end'
-- UNION ALL
-- SELECT 'New exercise_plan_completed count', COUNT(*)
-- FROM workout_events WHERE event_type = 'exercise_plan_completed';


-- =============================================================================
-- Rollback Script (if needed)
-- =============================================================================

-- To rollback the data migration (not the table creation):
-- DELETE FROM workout_events;

-- To completely rollback including table:
-- Run: alembic downgrade -1
