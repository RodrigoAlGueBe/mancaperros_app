"""
Services package for mancaperros_app.

This package contains business logic services that encapsulate domain operations
and separate concerns from the API endpoints and data access layer.

Available Services:
- UserService: Handles user-related operations (authentication, profile management)
- ExercisePlanService: Handles exercise plan creation, assignment, and retrieval
- RoutineService: Handles routine operations and tracking workout completion
- TrackerService: Handles user progress tracking and statistics
"""

from app.domain.services.user_service import UserService, get_user_service
from app.domain.services.exercise_plan_service import (
    ExercisePlanService,
    get_exercise_plan_service,
)
from app.domain.services.routine_service import RoutineService, get_routine_service
from app.domain.services.tracker_service import TrackerService, get_tracker_service


__all__ = [
    # User Service
    "UserService",
    "get_user_service",
    # Exercise Plan Service
    "ExercisePlanService",
    "get_exercise_plan_service",
    # Routine Service
    "RoutineService",
    "get_routine_service",
    # Tracker Service
    "TrackerService",
    "get_tracker_service",
]
