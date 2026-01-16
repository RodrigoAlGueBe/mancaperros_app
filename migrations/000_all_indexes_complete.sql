-- Migration: Complete Database Indexes
-- Created: 2026-01-11
-- Description: Complete set of all recommended performance indexes for the mancaperros_app database
-- Note: This is a reference file with all indexes. Some may already exist from previous migrations.

-- ============================================
-- ALL RECOMMENDED INDEXES
-- ============================================

-- Tabla users
-- Purpose: Optimize queries filtering/searching by email and username
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_user_name ON users(user_name);

-- Tabla exercise_plans
-- Purpose: Optimize queries filtering by user owner and exercise plan type
CREATE INDEX IF NOT EXISTS idx_exercise_plans_user_owner_id ON exercise_plans(user_owner_id);
CREATE INDEX IF NOT EXISTS idx_exercise_plans_type ON exercise_plans(exercise_plan_type);

-- Tabla rutines
-- Purpose: Optimize queries joining with exercise_plans and filtering by plan+group
CREATE INDEX IF NOT EXISTS idx_rutines_exercise_plan_id ON rutines(exercise_plan_id);
CREATE INDEX IF NOT EXISTS idx_rutines_plan_group ON rutines(exercise_plan_id, rutine_group);

-- Tabla exercises
-- Purpose: Optimize queries joining with rutines
CREATE INDEX IF NOT EXISTS idx_exercises_rutine_id ON exercises(rutine_id);

-- Tabla user_tracker
-- Purpose: Optimize queries filtering by user and user+info_type combination
CREATE INDEX IF NOT EXISTS idx_user_tracker_user_id ON user_tracker(user_id);
CREATE INDEX IF NOT EXISTS idx_user_tracker_user_type ON user_tracker(user_id, info_type);

-- ============================================
-- VERIFY CREATED INDEXES (SQLite)
-- ============================================
-- Run this query to see all indexes:
-- SELECT
--     m.name as index_name,
--     m.tbl_name as table_name,
--     m.sql as definition
-- FROM sqlite_master m
-- WHERE m.type = 'index'
--   AND m.name LIKE 'idx_%'
-- ORDER BY m.tbl_name, m.name;

-- ============================================
-- INDEX USAGE ANALYSIS
-- ============================================
-- These indexes will improve performance for common query patterns:
--
-- 1. idx_users_email, idx_users_user_name
--    - User login/authentication queries
--    - User search operations
--
-- 2. idx_exercise_plans_user_owner_id
--    - Fetch all exercise plans for a specific user
--    - User's exercise plan dashboard
--
-- 3. idx_exercise_plans_type
--    - Filter exercise plans by type (e.g., strength, cardio, flexibility)
--    - Exercise plan categorization and filtering
--
-- 4. idx_rutines_exercise_plan_id
--    - Fetch all rutines for a specific exercise plan
--    - Exercise plan detail view
--
-- 5. idx_rutines_plan_group (composite index)
--    - Queries filtering by both exercise_plan_id AND rutine_group
--    - More efficient than single-column index for combined queries
--
-- 6. idx_exercises_rutine_id
--    - Fetch all exercises for a specific rutine
--    - Rutine detail view
--
-- 7. idx_user_tracker_user_id
--    - Fetch all tracking data for a specific user
--    - User progress dashboard
--
-- 8. idx_user_tracker_user_type (composite index)
--    - Queries filtering by both user_id AND info_type
--    - Fetch specific tracking metrics for a user

-- ============================================
-- COMPLETE DOWNGRADE (REMOVE ALL INDEXES)
-- ============================================
-- Uncomment to remove all indexes:
-- DROP INDEX IF EXISTS idx_users_email;
-- DROP INDEX IF EXISTS idx_users_user_name;
-- DROP INDEX IF EXISTS idx_exercise_plans_user_owner_id;
-- DROP INDEX IF EXISTS idx_exercise_plans_type;
-- DROP INDEX IF EXISTS idx_rutines_exercise_plan_id;
-- DROP INDEX IF EXISTS idx_rutines_plan_group;
-- DROP INDEX IF EXISTS idx_exercises_rutine_id;
-- DROP INDEX IF EXISTS idx_user_tracker_user_id;
-- DROP INDEX IF EXISTS idx_user_tracker_user_type;
