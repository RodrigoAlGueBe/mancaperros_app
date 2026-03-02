# Re-export all ORM models for backward compatibility
from database import Base
from models.orm.user import User
from models.orm.exercise_plan import Exercise_plan, Exercise_plan_global
from models.orm.rutine import Rutine, Rutine_global
from models.orm.exercise import Exsercise, Exsercise_global
from models.orm.user_tracker import User_Tracker

# Re-export Pydantic auth models (kept here for backward compatibility)
from schemas.auth import Token, TokenData

__all__ = [
    "User",
    "Exercise_plan",
    "Exercise_plan_global",
    "Rutine",
    "Rutine_global",
    "Exsercise",
    "Exsercise_global",
    "User_Tracker",
    "Token",
    "TokenData",
]
