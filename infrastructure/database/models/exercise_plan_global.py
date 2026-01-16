"""
Exercise Plan Global model definition.

This module defines the Exercise_plan_global SQLAlchemy model for
global exercise plan templates.
"""

from datetime import date

from sqlalchemy import Column, ForeignKey, Integer, String, Date, JSON
from sqlalchemy.orm import relationship

from infrastructure.database.models.base import Base
import settings


class Exercise_plan_global(Base):
    """
    Global Exercise Plan model representing exercise plan templates.

    Global exercise plans serve as templates that can be assigned to users.
    They are created by administrators or users and can be shared.

    Attributes:
        exercise_plan_id: Primary key identifier
        exercise_plan_name: Name of the exercise plan
        user_creator_id: Foreign key to the creating user
        exercise_plan_type: Type classification of the plan
        creation_date: Date when the plan was created
        difficult_level: Difficulty classification
        routine_group_order: JSON array defining routine order

    Relationships:
        rutines: List of global routines in this plan
        exercise_plan_owner: The user who created this plan
    """
    __tablename__ = "exercise_plans_global"

    exercise_plan_id = Column(Integer, primary_key=True, index=True)
    exercise_plan_name = Column(
        String(255),
        nullable=False,
        unique=False,
        index=True,
        default="New exercise plan"
    )
    user_creator_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )
    exercise_plan_type = Column(
        String(255),
        nullable=False,
        unique=False,
        index=True,
        default="New exercise plan type"
    )
    creation_date = Column(
        Date,
        nullable=False,
        unique=False,
        index=True,
        default=date(1970, 1, 1)
    )
    difficult_level = Column(
        String(255),
        nullable=False,
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
        "Rutine_global",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    exercise_plan_owner = relationship(
        "User",
        back_populates="exercise_plan_global"
    )
