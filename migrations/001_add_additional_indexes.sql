-- Migration: Add Additional Database Indexes
-- Created: 2026-01-11
-- Description: Adds additional performance indexes for exercise_plans, rutines, and user_tracker tables
-- Dependencies: Assumes tables users, exercise_plans, rutines, exercises, and user_tracker exist

-- ============================================
-- UPGRADE
-- ============================================

-- Tabla users (estos ya deberían existir de la migración anterior, pero se incluyen por completitud)
-- CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
-- CREATE INDEX IF NOT EXISTS idx_users_user_name ON users(user_name);

-- Tabla exercise_plans
-- CREATE INDEX IF NOT EXISTS idx_exercise_plans_user_owner_id ON exercise_plans(user_owner_id);
CREATE INDEX IF NOT EXISTS idx_exercise_plans_type ON exercise_plans(exercise_plan_type);

-- Tabla rutines
-- CREATE INDEX IF NOT EXISTS idx_rutines_exercise_plan_id ON rutines(exercise_plan_id);
CREATE INDEX IF NOT EXISTS idx_rutines_plan_group ON rutines(exercise_plan_id, rutine_group);

-- Tabla exercises (este ya debería existir de la migración anterior)
-- CREATE INDEX IF NOT EXISTS idx_exercises_rutine_id ON exercises(rutine_id);

-- Tabla user_tracker
-- CREATE INDEX IF NOT EXISTS idx_user_tracker_user_id ON user_tracker(user_id);
CREATE INDEX IF NOT EXISTS idx_user_tracker_user_type ON user_tracker(user_id, info_type);

-- ============================================
-- VERIFICAR ÍNDICES CREADOS
-- ============================================
-- Para SQLite, puedes verificar los índices con:
-- SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' ORDER BY tbl_name, name;

-- ============================================
-- DOWNGRADE (para revertir los cambios)
-- ============================================
-- DROP INDEX IF EXISTS idx_exercise_plans_type;
-- DROP INDEX IF EXISTS idx_rutines_plan_group;
-- DROP INDEX IF EXISTS idx_user_tracker_user_type;
