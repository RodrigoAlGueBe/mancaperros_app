"""
Routine Global model definition.

This module defines the Rutine_global SQLAlchemy model for global
routine templates.
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from infrastructure.database.models.base import Base


class Rutine_global(Base):
    """
    Global Routine model representing routine templates.

    Global routines are part of global exercise plans and serve as
    templates for user-specific routines.

    Attributes:
        rutine_id: Primary key identifier
        rutine_name: Name of the routine
        rutine_type: Type classification
        rutine_group: Muscle group or workout focus
        rutine_category: Category classification
        exercise_plan_id: Foreign key to parent global exercise plan
        rounds: Number of rounds/sets to perform
        rst_btw_exercises: Rest time between exercises (as string)
        rst_btw_rounds: Rest time between rounds (as string)
        difficult_level: Difficulty classification

    Relationships:
        owner: Parent global exercise plan
        exercises: List of global exercises in this routine
    """
    __tablename__ = "rutines_global"

    rutine_id = Column(Integer, primary_key=True, index=True)
    rutine_name = Column(
        String(255),
        nullable=False,
        unique=False,
        index=True,
        default="New rutine name"
    )
    rutine_type = Column(
        String(255),
        nullable=False,
        unique=False,
        index=True,
        default="New rutine type"
    )
    rutine_group = Column(
        String(255),
        nullable=False,
        unique=False,
        index=True,
        default="New rutine group"
    )
    rutine_category = Column(
        String(255),
        nullable=False,
        unique=False,
        index=True,
        default="New rutine category"
    )
    exercise_plan_id = Column(
        Integer,
        ForeignKey("exercise_plans_global.exercise_plan_id"),
        nullable=False
    )
    rounds = Column(
        Integer,
        nullable=False,
        unique=False,
        index=True,
        default=0
    )
    rst_btw_exercises = Column(
        String(255),
        nullable=False,
        unique=False,
        index=True,
        default="0"
    )
    rst_btw_rounds = Column(
        String(255),
        nullable=False,
        unique=False,
        index=True,
        default="0"
    )
    difficult_level = Column(
        String(255),
        nullable=False,
        unique=False,
        index=True,
        default="New rutine difficult level"
    )

    # Relationships
    owner = relationship("Exercise_plan_global", back_populates="rutines")
    exercises = relationship(
        "Exercise_global",
        back_populates="exercise_owner",
        cascade="all, delete-orphan"
    )
