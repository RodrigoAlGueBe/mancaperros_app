"""
Models compatibility module.

This module re-exports all models from the new infrastructure location
to maintain backward compatibility with existing imports.

DEPRECATED: Import models directly from infrastructure.database.models instead:
    from infrastructure.database.models import User, Exercise_plan, ...
"""

# Re-export Base from the new location
from infrastructure.database.models.base import Base

# Re-export all models for backward compatibility
from infrastructure.database.models.user import User
from infrastructure.database.models.exercise_plan import Exercise_plan
from infrastructure.database.models.routine import Rutine
from infrastructure.database.models.exercise import Exercise
from infrastructure.database.models.exercise_plan_global import Exercise_plan_global
from infrastructure.database.models.routine_global import Rutine_global
from infrastructure.database.models.exercise_global import Exercise_global
from infrastructure.database.models.user_tracker import User_Tracker
from infrastructure.database.models.auth import Token, TokenData

# New polymorphic workout event models (HIGH-08 refactoring)
from infrastructure.database.models.workout_event import (
    WorkoutEvent,
    RoutineCompletedEvent,
    ExercisePlanStartedEvent,
    ExercisePlanCompletedEvent,
)


__all__ = [
    "Base",
    "User",
    "Exercise_plan",
    "Rutine",
    "Exercise",
    "Exercise_plan_global",
    "Rutine_global",
    "Exercise_global",
    # Legacy model - kept for backward compatibility
    "User_Tracker",
    # New polymorphic event models
    "WorkoutEvent",
    "RoutineCompletedEvent",
    "ExercisePlanStartedEvent",
    "ExercisePlanCompletedEvent",
    "Token",
    "TokenData",
]
