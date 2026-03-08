from __future__ import annotations
from pydantic import BaseModel
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.rutine import Rutine, Rutine_global


class Exercise_plan_Base(BaseModel):
    exercise_plan_name: str


class Exercise_plan_Create(Exercise_plan_Base):
    exercise_plan_type: str | None = None
    difficult_level: str | None = None
    user_owner_id: int
    creation_date: date | None = None

    rutines: list[Rutine] = []


class Exercise_plan(Exercise_plan_Base):
    user_owner_id: int
    exercise_plan_type: str | None = None
    difficult_level: str | None = None

    rutines: list[Rutine] = []

    class Config:
        from_attributes = True


class Exercise_plan_global_Base(BaseModel):
    exercise_plan_name: str


class Exercise_plan_global_info(Exercise_plan_global_Base):
    exercise_plan_id: int


class Exercise_plan_global_Response(Exercise_plan_global_Base):
    exercise_plan_id: int
    exercise_plan_type: str | None = None
    difficult_level: str | None = None
    creation_date: date | None = None

    class Config:
        from_attributes = True


class Exercise_plan_global_Create(Exercise_plan_global_Base):
    exercise_plan_type: str | None = None
    difficult_level: str | None = None


class Exercise_plan_global(Exercise_plan_global_Base):
    user_creator_id: int
    exercise_plan_type: str | None = None
    difficult_level: str | None = None
    creation_date: date | None = None

    rutines: list[Rutine_global] = []

    class Config:
        from_attributes = True
