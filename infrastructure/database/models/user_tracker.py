"""
User Tracker model definition.

This module defines the User_Tracker SQLAlchemy model for tracking
user activities and progress.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship

from infrastructure.database.models.base import Base


class User_Tracker(Base):
    """
    User Tracker model for recording user activities and progress.

    This model tracks various user activities including exercise plan
    starts/ends, routine completions, and exercise progress metrics.

    Attributes:
        user_tracker_id: Primary key identifier
        user_id: Foreign key to the tracked user
        record_datetime: Timestamp of the record
        info_type: Type of activity (e.g., "exercise_plan_start", "rutine_end")
        info_description: Additional description or identifier
        exercise_increments: JSON with per-exercise increment data
        push_increment: Total push exercise increment
        pull_increment: Total pull exercise increment
        isometric_increment: Total isometric exercise increment
        push_time_increment: Total push time increment
        pull_time_increment: Total pull time increment
        isometric_time_increment: Total isometric time increment

    Relationships:
        user_tracked: The user being tracked
    """
    __tablename__ = "users_tracker"

    user_tracker_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )
    record_datetime = Column(
        DateTime,
        nullable=False,
        unique=False,
        index=True,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    info_type = Column(
        String(255),
        nullable=False,
        unique=False,
        index=True,
        default="Non_specifed"
    )
    info_description = Column(
        String(255),
        nullable=True,
        unique=False,
        index=True,
        default="Non_specifed"
    )
    exercise_increments = Column(JSON, nullable=True, unique=False, default=None)
    push_increment = Column(Integer, nullable=False, unique=False, default=0)
    pull_increment = Column(Integer, nullable=False, unique=False, default=0)
    isometric_increment = Column(Integer, nullable=False, unique=False, default=0)
    push_time_increment = Column(Integer, nullable=False, unique=False, default=0)
    pull_time_increment = Column(Integer, nullable=False, unique=False, default=0)
    isometric_time_increment = Column(Integer, nullable=False, unique=False, default=0)

    # Relationships
    user_tracked = relationship("User", back_populates="user_tracker")
