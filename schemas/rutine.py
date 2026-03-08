from __future__ import annotations
from pydantic import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.exercise import Exercise_global


class Rutine_Base(BaseModel):
    rutine_name: str
    rutine_type: str | None = None
    rutine_group: str | None = None
    rutine_category: str | None = None


class Rutine_Create(Rutine_Base):
    pass


class Rutine(Rutine_Base):
    rutine_id: int
    exercise_plan_id: int

    class Config:
        from_attributes = True


class Rutine_global_Base(BaseModel):
    rutine_name: str


class Rutine_global_Create(Rutine_global_Base):
    exercise_plan_id: int
    rutine_type: str | None = None
    rutine_group: str | None = None
    rutine_category: str | None = None
    rounds: int
    rst_btw_exercises: str
    rst_btw_rounds: str
    difficult_level: str | None = None


class Rutine_global(Rutine_global_Base):
    rounds: int
    rst_btw_exercises: str
    rst_btw_rounds: str
    difficult_level: str | None = None

    exercises: list[Exercise_global] = []

    class Config:
        from_attributes = True
