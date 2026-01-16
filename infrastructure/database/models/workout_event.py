"""
Workout Event models with Single Table Inheritance.

This module defines a polymorphic event system using SQLAlchemy's Single Table Inheritance
to replace the overloaded User_Tracker table. Each event type has its own specialized
subclass with type-specific fields.

Design Rationale:
-----------------
The previous User_Tracker model used a discriminator column (info_type) with conditional
fields that were only valid for certain event types. This led to:
- Nullable fields that should be required for specific event types
- No type safety at the ORM level
- Difficulty in adding new event types without affecting existing code

The new design uses SQLAlchemy's polymorphic identity pattern:
- Base WorkoutEvent class defines common fields
- Specialized subclasses define event-specific fields
- SQLAlchemy automatically handles type discrimination
- Type-safe queries for specific event types

BACKWARD COMPATIBILITY:
-----------------------
The old User_Tracker model and users_tracker table are preserved.
This new table (workout_events) coexists with the old one during migration.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship

from infrastructure.database.models.base import Base


class WorkoutEvent(Base):
    """
    Base class for all workout-related events using Single Table Inheritance.

    This is the parent class in a polymorphic hierarchy. The event_type column
    serves as the discriminator to determine the actual Python class for each row.

    Attributes:
        event_id: Primary key identifier
        user_id: Foreign key to the user who generated this event
        event_type: Discriminator column for polymorphic identity
        timestamp: When the event occurred (defaults to current UTC time)

    Relationships:
        user: The user who generated this event
    """
    __tablename__ = "workout_events"

    event_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    event_type = Column(String(50), nullable=False, index=True)
    timestamp = Column(
        DateTime,
        nullable=False,
        index=True,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    # Fields for RoutineCompletedEvent (nullable at base level for STI)
    routine_group = Column(String(255), nullable=True, index=True)
    exercise_increments = Column(JSON, nullable=True)
    push_increment = Column(Integer, nullable=True, default=0)
    pull_increment = Column(Integer, nullable=True, default=0)
    isometric_increment = Column(Integer, nullable=True, default=0)
    push_time_increment = Column(Integer, nullable=True, default=0)
    pull_time_increment = Column(Integer, nullable=True, default=0)
    isometric_time_increment = Column(Integer, nullable=True, default=0)

    # Fields for ExercisePlan events (nullable at base level for STI)
    exercise_plan_id = Column(Integer, nullable=True, index=True)

    # Relationship to User
    user = relationship("User", back_populates="workout_events")

    __mapper_args__ = {
        "polymorphic_on": event_type,
        "polymorphic_identity": "workout_event"
    }

    def __repr__(self) -> str:
        return (
            f"<WorkoutEvent(event_id={self.event_id}, user_id={self.user_id}, "
            f"type={self.event_type}, timestamp={self.timestamp})>"
        )


class RoutineCompletedEvent(WorkoutEvent):
    """
    Event recorded when a user completes a workout routine.

    This event captures detailed progress information including:
    - Which routine group was completed
    - Individual exercise increments (as JSON)
    - Aggregated increments by exercise type (push, pull, isometric)
    - Time increments for timed exercises

    The routine_group field maps to the previous info_description field,
    representing the muscular group or routine category completed.
    """

    __mapper_args__ = {
        "polymorphic_identity": "routine_completed"
    }

    def __repr__(self) -> str:
        return (
            f"<RoutineCompletedEvent(event_id={self.event_id}, user_id={self.user_id}, "
            f"routine_group={self.routine_group}, timestamp={self.timestamp})>"
        )


class ExercisePlanStartedEvent(WorkoutEvent):
    """
    Event recorded when a user starts a new exercise plan.

    This event marks the beginning of a workout program for a user.
    The exercise_plan_id links to the specific plan being started.
    """

    __mapper_args__ = {
        "polymorphic_identity": "exercise_plan_started"
    }

    def __repr__(self) -> str:
        return (
            f"<ExercisePlanStartedEvent(event_id={self.event_id}, user_id={self.user_id}, "
            f"exercise_plan_id={self.exercise_plan_id}, timestamp={self.timestamp})>"
        )


class ExercisePlanCompletedEvent(WorkoutEvent):
    """
    Event recorded when a user completes an exercise plan.

    This event marks the end of a workout program cycle. Combined with
    ExercisePlanStartedEvent, it allows tracking of complete workout cycles.
    """

    __mapper_args__ = {
        "polymorphic_identity": "exercise_plan_completed"
    }

    def __repr__(self) -> str:
        return (
            f"<ExercisePlanCompletedEvent(event_id={self.event_id}, user_id={self.user_id}, "
            f"exercise_plan_id={self.exercise_plan_id}, timestamp={self.timestamp})>"
        )


# Type alias for any workout event type (useful for type hints)
AnyWorkoutEvent = (
    WorkoutEvent
    | RoutineCompletedEvent
    | ExercisePlanStartedEvent
    | ExercisePlanCompletedEvent
)
