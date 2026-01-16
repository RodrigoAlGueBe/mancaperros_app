"""
Routine model definition.

This module defines the Rutine SQLAlchemy model for user-specific routines.
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from infrastructure.database.models.base import Base
from infrastructure.database.models.soft_delete_mixin import SoftDeleteMixin


class Rutine(Base, SoftDeleteMixin):
    """
    Routine model representing a workout routine within an exercise plan.

    A routine contains multiple exercises and defines parameters like
    rounds, rest times, and categorization.

    Attributes:
        rutine_id: Primary key identifier
        rutine_name: Name of the routine
        rutine_type: Type classification
        rutine_group: Muscle group or workout focus
        rutine_category: Category classification
        exercise_plan_id: Foreign key to parent exercise plan
        rounds: Number of rounds/sets to perform
        rst_btw_exercises: Rest time between exercises (as string)
        rst_btw_rounds: Rest time between rounds (as string)
        difficult_level: Difficulty classification

    Relationships:
        owner: Parent exercise plan
        exercises: List of exercises in this routine
    """
    __tablename__ = "rutines"

    rutine_id = Column(Integer, primary_key=True, index=True)
    rutine_name = Column(
        String(255),
        unique=False,
        index=True,
        default="New rutine name"
    )
    rutine_type = Column(
        String(255),
        unique=False,
        index=True,
        default="New rutine type"
    )
    rutine_group = Column(
        String(255),
        unique=False,
        index=True,
        default="New rutine group"
    )
    rutine_category = Column(
        String(255),
        unique=False,
        index=True,
        default="New rutine category"
    )
    exercise_plan_id = Column(
        Integer,
        ForeignKey("exercise_plans.exercise_plan_id")
    )
    rounds = Column(Integer, unique=False, index=True, default=0)
    rst_btw_exercises = Column(
        String(255),
        unique=False,
        index=True,
        default="0"
    )
    rst_btw_rounds = Column(
        String(255),
        unique=False,
        index=True,
        default="0"
    )
    difficult_level = Column(
        String(255),
        unique=False,
        index=True,
        default="New rutine difficult level"
    )

    # Relationships
    owner = relationship("Exercise_plan", back_populates="rutines")
    exercises = relationship(
        "Exercise",
        back_populates="exercise_owner",
        cascade="all, delete-orphan"
    )
