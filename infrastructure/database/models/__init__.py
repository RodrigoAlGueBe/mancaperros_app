"""
Database models package.

This package contains all SQLAlchemy ORM models for the application.
Models are organized by domain and exported here for convenient imports.
"""

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

# Mixins for reducing model duplication (MED-08 refactoring)
from infrastructure.database.models.mixins import (
    ExercisePlanMixin,
    RoutineMixin,
    ExerciseMixin,
)

# Soft delete mixin
from infrastructure.database.models.soft_delete_mixin import SoftDeleteMixin

__all__ = [
    # Core models
    "User",
    "Exercise_plan",
    "Rutine",
    "Exercise",
    "Exercise_plan_global",
    "Rutine_global",
    "Exercise_global",
    # Legacy model - kept for backward compatibility
    "User_Tracker",
    # New polymorphic event models (HIGH-08)
    "WorkoutEvent",
    "RoutineCompletedEvent",
    "ExercisePlanStartedEvent",
    "ExercisePlanCompletedEvent",
    # Auth models
    "Token",
    "TokenData",
    # Mixins (MED-08)
    "ExercisePlanMixin",
    "RoutineMixin",
    "ExerciseMixin",
    "SoftDeleteMixin",
]
