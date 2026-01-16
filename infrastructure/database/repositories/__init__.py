"""
Repository implementations package.

This package contains all repository classes that encapsulate
database operations for different domain entities.
"""

from infrastructure.database.repositories.base_repository import BaseRepository
from infrastructure.database.repositories.user_repository import UserRepository
from infrastructure.database.repositories.exercise_plan_repository import ExercisePlanRepository
from infrastructure.database.repositories.routine_repository import RoutineRepository
from infrastructure.database.repositories.exercise_repository import ExerciseRepository
from infrastructure.database.repositories.tracker_repository import TrackerRepository
from infrastructure.database.repositories.exercise_plan_global_repository import ExercisePlanGlobalRepository
from infrastructure.database.repositories.routine_global_repository import RoutineGlobalRepository
from infrastructure.database.repositories.exercise_global_repository import ExerciseGlobalRepository

# New polymorphic workout event repository (HIGH-08 refactoring)
from infrastructure.database.repositories.workout_event_repository import WorkoutEventRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "ExercisePlanRepository",
    "RoutineRepository",
    "ExerciseRepository",
    # Legacy repository - kept for backward compatibility
    "TrackerRepository",
    # New polymorphic event repository
    "WorkoutEventRepository",
    "ExercisePlanGlobalRepository",
    "RoutineGlobalRepository",
    "ExerciseGlobalRepository",
]
