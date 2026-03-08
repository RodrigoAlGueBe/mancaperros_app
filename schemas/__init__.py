from __future__ import annotations

# Re-export all schemas for backward compatibility
from schemas.auth import Token, TokenData
from schemas.user import User_Base, User_Create, User_Information, User
from schemas.exercise import Exercise_Base, Exercise_Create, Exercise, Exercise_global_Base, Exercise_global_Create, Exercise_global
from schemas.rutine import Rutine_Base, Rutine_Create, Rutine, Rutine_global_Base, Rutine_global_Create, Rutine_global
from schemas.exercise_plan import (
    Exercise_plan_Base, Exercise_plan_Create, Exercise_plan,
    Exercise_plan_global_Base, Exercise_plan_global_info, Exercise_plan_global_Response,
    Exercise_plan_global_Create, Exercise_plan_global
)
from schemas.user_tracker import User_tracker_Base, User_tracker_exercise_plan

# Update forward refs
Exercise_plan_global.model_rebuild()
Rutine_global.model_rebuild()

__all__ = [
    "Token", "TokenData",
    "User_Base", "User_Create", "User_Information", "User",
    "Exercise_Base", "Exercise_Create", "Exercise",
    "Exercise_global_Base", "Exercise_global_Create", "Exercise_global",
    "Rutine_Base", "Rutine_Create", "Rutine",
    "Rutine_global_Base", "Rutine_global_Create", "Rutine_global",
    "Exercise_plan_Base", "Exercise_plan_Create", "Exercise_plan",
    "Exercise_plan_global_Base", "Exercise_plan_global_info",
    "Exercise_plan_global_Response", "Exercise_plan_global_Create", "Exercise_plan_global",
    "User_tracker_Base", "User_tracker_exercise_plan",
]
