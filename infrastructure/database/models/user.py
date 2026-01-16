"""
User model definition.

This module defines the User SQLAlchemy model for user management.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from infrastructure.database.models.base import Base
from infrastructure.database.models.soft_delete_mixin import SoftDeleteMixin


class User(Base, SoftDeleteMixin):
    """
    User model representing application users.

    Attributes:
        user_id: Primary key identifier
        user_name: Username for login
        email: User's email address (unique)
        hashed_password: Bcrypt hashed password
        user_image: Path to user's profile image

    Relationships:
        exercise_plan: User's personal exercise plan
        exercise_plan_global: Global exercise plans created by user
        user_tracker: User's activity tracking records (legacy)
        workout_events: User's workout events (new polymorphic model)
    """
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(255), unique=False, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255), unique=False, index=True)
    user_image = Column(String(255), unique=False, index=True, default="empty")

    # Relationships
    exercise_plan = relationship(
        "Exercise_plan",
        back_populates="exercise_plan_owner",
        cascade="all, delete-orphan"
    )
    exercise_plan_global = relationship(
        "Exercise_plan_global",
        back_populates="exercise_plan_owner"
    )
    # Legacy relationship - kept for backward compatibility
    user_tracker = relationship(
        "User_Tracker",
        back_populates="user_tracked"
    )
    # New polymorphic workout events relationship
    workout_events = relationship(
        "WorkoutEvent",
        back_populates="user",
        cascade="all, delete-orphan"
    )
