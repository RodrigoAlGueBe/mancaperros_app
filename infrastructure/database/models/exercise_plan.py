"""
Exercise Plan model definition.

This module defines the Exercise_plan SQLAlchemy model for user-specific
exercise plans.
"""

from datetime import date

from sqlalchemy import Column, ForeignKey, Integer, String, Date, JSON
from sqlalchemy.orm import relationship

from infrastructure.database.models.base import Base
from infrastructure.database.models.soft_delete_mixin import SoftDeleteMixin
import settings


class Exercise_plan(Base, SoftDeleteMixin):
    """
    Exercise Plan model representing a user's personal exercise plan.

    This is a copy of a global exercise plan assigned to a specific user,
    allowing personalization of routines and exercises.

    Attributes:
        exercise_plan_id: Primary key identifier
        exercise_plan_name: Name of the exercise plan
        user_owner_id: Foreign key to the owning user
        exercise_plan_type: Type classification of the plan
        creation_date: Date when the plan was created/assigned
        difficult_level: Difficulty classification
        routine_group_order: JSON array defining routine order

    Relationships:
        rutines: List of routines in this plan
        exercise_plan_owner: The user who owns this plan
    """
    __tablename__ = "exercise_plans"

    exercise_plan_id = Column(Integer, primary_key=True, index=True)
    exercise_plan_name = Column(
        String(255),
        unique=False,
        index=True,
        default="New exercise plan"
    )
    user_owner_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=True
    )
    exercise_plan_type = Column(
        String(255),
        unique=False,
        index=True,
        default="New exercise plan type"
    )
    creation_date = Column(
        Date,
        unique=False,
        index=True,
        default=date(1970, 1, 1)
    )
    difficult_level = Column(
        String(255),
        unique=False,
        index=True,
        default="New exercise plan difficult level"
    )
    routine_group_order = Column(
        JSON,
        nullable=False,
        unique=False,
        default=settings.ROUTINE_GROUP_ORDER_DEFAULT
    )

    # Relationships
    rutines = relationship(
        "Rutine",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    exercise_plan_owner = relationship(
        "User",
        back_populates="exercise_plan"
    )
