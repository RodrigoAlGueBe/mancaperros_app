"""
Domain-Specific Mixins for Exercise Plans, Routines, and Exercises.

This module provides reusable mixin classes that consolidate common fields
and behavior shared between user-specific and global models. These mixins
reduce code duplication and ensure consistency across model definitions.

Mixins follow SQLAlchemy 2.0+ best practices using @declared_attr for
column definitions, making them compatible with both joined table inheritance
and multiple inheritance patterns.

Architecture:
- ExercisePlanMixin: Common fields for Exercise_plan and Exercise_plan_global
- RoutineMixin: Common fields for Rutine and Rutine_global
- ExerciseMixin: Common fields for Exercise and Exercise_global

These mixins extract ~95% of duplicated logic, supporting a ~47% reduction
in code duplication when applied to existing models.

Usage Example:
    from infrastructure.database.models.mixins import ExercisePlanMixin
    from infrastructure.database.models.base import Base

    class Exercise_plan(Base, SoftDeleteMixin, ExercisePlanMixin):
        __tablename__ = "exercise_plans"

        exercise_plan_id = Column(Integer, primary_key=True, index=True)
        # user_owner_id is specific to this model, not in mixin
        user_owner_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)

        # All common fields are inherited from ExercisePlanMixin:
        # - exercise_plan_name
        # - exercise_plan_type
        # - creation_date
        # - difficult_level
        # - routine_group_order

MED-08 Analysis Reference:
    - Exercise_plan vs Exercise_plan_global: 90-95% field duplication
    - Rutine vs Rutine_global: 90-95% field duplication
    - Exercise vs Exercise_global: 90-95% field duplication
"""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import Column, Integer, String, Date, JSON
from sqlalchemy.orm import declared_attr

import settings


__all__ = [
    "ExercisePlanMixin",
    "RoutineMixin",
    "ExerciseMixin",
]


class ExercisePlanMixin:
    """
    Mixin providing common fields for exercise plan models.

    Consolidates shared attributes between Exercise_plan (user-specific)
    and Exercise_plan_global (global templates). These fields define the
    core structure and metadata of an exercise plan.

    Common Fields (5 total):
        exercise_plan_name: Name of the exercise plan (String, 255)
        exercise_plan_type: Type classification of the plan (String, 255)
        creation_date: Date when the plan was created (Date)
        difficult_level: Difficulty classification (String, 255)
        routine_group_order: JSON array defining routine order (JSON)

    Fields NOT included (model-specific):
        - exercise_plan_id: Primary key (each model defines its own)
        - user_owner_id/user_creator_id: Foreign key to users (different semantics)
        - Relationships: Different back_populates for each model

    Notes:
        - Different models have different nullability constraints; subclasses
          should override columns if needed with nullable=True/False
        - Defaults are consistent across models for better data integrity
        - routine_group_order uses settings.ROUTINE_GROUP_ORDER_DEFAULT
    """

    @declared_attr
    def exercise_plan_name(cls) -> Column[str]:
        """Name of the exercise plan."""
        return Column(
            String(255),
            unique=False,
            index=True,
            default="New exercise plan",
            doc="Descriptive name of the exercise plan"
        )

    @declared_attr
    def exercise_plan_type(cls) -> Column[str]:
        """Type classification of the exercise plan."""
        return Column(
            String(255),
            unique=False,
            index=True,
            default="New exercise plan type",
            doc="Classification type (e.g., strength, cardio, flexibility)"
        )

    @declared_attr
    def creation_date(cls) -> Column[date]:
        """Date when the exercise plan was created."""
        return Column(
            Date,
            unique=False,
            index=True,
            default=date(1970, 1, 1),
            doc="Date when the plan was created or assigned"
        )

    @declared_attr
    def difficult_level(cls) -> Column[str]:
        """Difficulty classification of the exercise plan."""
        return Column(
            String(255),
            unique=False,
            index=True,
            default="New exercise plan difficult level",
            doc="Difficulty level (e.g., beginner, intermediate, advanced)"
        )

    @declared_attr
    def routine_group_order(cls) -> Column[Any]:
        """JSON array defining the order of routine groups."""
        return Column(
            JSON,
            nullable=False,
            unique=False,
            default=settings.ROUTINE_GROUP_ORDER_DEFAULT,
            doc="JSON array specifying the order and grouping of routines"
        )


class RoutineMixin:
    """
    Mixin providing common fields for routine models.

    Consolidates shared attributes between Rutine (user-specific) and
    Rutine_global (global templates). These fields define the structure
    and parameters of a workout routine.

    Common Fields (8 total):
        rutine_name: Name of the routine (String, 255)
        rutine_type: Type classification (String, 255)
        rutine_group: Muscle group or workout focus (String, 255)
        rutine_category: Category classification (String, 255)
        rounds: Number of rounds/sets (Integer)
        rst_btw_exercises: Rest time between exercises (String, 255)
        rst_btw_rounds: Rest time between rounds (String, 255)
        difficult_level: Difficulty classification (String, 255)

    Fields NOT included (model-specific):
        - rutine_id: Primary key (each model defines its own)
        - exercise_plan_id: Foreign key references different tables
          (exercise_plans vs exercise_plans_global)
        - Relationships: Different back_populates for each model

    Notes:
        - Rest times are stored as strings for flexibility in format
          (e.g., "30", "1:30", "30s")
        - Different models have different nullability constraints;
          override columns as needed
    """

    @declared_attr
    def rutine_name(cls) -> Column[str]:
        """Name of the routine."""
        return Column(
            String(255),
            unique=False,
            index=True,
            default="New rutine name",
            doc="Descriptive name of the routine"
        )

    @declared_attr
    def rutine_type(cls) -> Column[str]:
        """Type classification of the routine."""
        return Column(
            String(255),
            unique=False,
            index=True,
            default="New rutine type",
            doc="Classification type (e.g., circuit, HIIT, steady-state)"
        )

    @declared_attr
    def rutine_group(cls) -> Column[str]:
        """Muscle group or workout focus of the routine."""
        return Column(
            String(255),
            unique=False,
            index=True,
            default="New rutine group",
            doc="Muscle group or body part focus"
        )

    @declared_attr
    def rutine_category(cls) -> Column[str]:
        """Category classification of the routine."""
        return Column(
            String(255),
            unique=False,
            index=True,
            default="New rutine category",
            doc="Categorical classification for organization"
        )

    @declared_attr
    def rounds(cls) -> Column[int]:
        """Number of rounds or sets in the routine."""
        return Column(
            Integer,
            unique=False,
            index=True,
            default=0,
            doc="Number of times to repeat the routine"
        )

    @declared_attr
    def rst_btw_exercises(cls) -> Column[str]:
        """Rest time between individual exercises."""
        return Column(
            String(255),
            unique=False,
            index=True,
            default="0",
            doc="Rest duration between exercises (flexible format)"
        )

    @declared_attr
    def rst_btw_rounds(cls) -> Column[str]:
        """Rest time between complete rounds."""
        return Column(
            String(255),
            unique=False,
            index=True,
            default="0",
            doc="Rest duration between rounds (flexible format)"
        )

    @declared_attr
    def difficult_level(cls) -> Column[str]:
        """Difficulty classification of the routine."""
        return Column(
            String(255),
            unique=False,
            index=True,
            default="New rutine difficult level",
            doc="Difficulty level (e.g., beginner, intermediate, advanced)"
        )


class ExerciseMixin:
    """
    Mixin providing common fields for exercise models.

    Consolidates shared attributes between Exercise (user-specific) and
    Exercise_global (global templates). These fields define the details
    of individual exercises within a routine.

    Common Fields (5 total):
        exercise_name: Name of the exercise (String, 255)
        rep: Repetitions or duration (String, 255)
        exercise_type: Type classification (String, 255)
        exercise_group: Muscle group targeted (String, 255)
        image: Path to exercise demonstration image (String, 255)

    Fields NOT included (model-specific):
        - exercise_id: Primary key (each model defines its own)
        - rutine_id: Foreign key references different tables
          (rutines vs rutines_global)
        - Relationships: Different back_populates for each model

    Notes:
        - rep field is a string to support flexible formats
          (e.g., "10", "30s", "until failure", "10-12")
        - Different models have different nullability constraints;
          override columns as needed
        - image field stores path or URL to demonstration media
    """

    @declared_attr
    def exercise_name(cls) -> Column[str]:
        """Name of the exercise."""
        return Column(
            String(255),
            unique=False,
            index=True,
            default="New exercise name",
            doc="Descriptive name of the exercise"
        )

    @declared_attr
    def rep(cls) -> Column[str]:
        """Repetitions or duration for the exercise."""
        return Column(
            String(255),
            unique=False,
            index=True,
            default="empty",
            doc="Repetitions, duration, or other rep format"
        )

    @declared_attr
    def exercise_type(cls) -> Column[str]:
        """Type classification of the exercise."""
        return Column(
            String(255),
            unique=False,
            index=True,
            default="New exercise type",
            doc="Classification type (e.g., push, pull, isometric)"
        )

    @declared_attr
    def exercise_group(cls) -> Column[str]:
        """Muscle group or body part targeted by the exercise."""
        return Column(
            String(255),
            unique=False,
            index=True,
            default="New exercise group",
            doc="Muscle group or body part targeted"
        )

    @declared_attr
    def image(cls) -> Column[str]:
        """Path to exercise demonstration image."""
        return Column(
            String(255),
            unique=False,
            index=True,
            default="empty",
            doc="Path or URL to demonstration image"
        )
