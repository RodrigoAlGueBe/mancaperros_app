"""
Workout Event Repository implementation.

This module provides data access operations for the new polymorphic WorkoutEvent
entities, offering type-safe methods for each event type.

This repository works alongside the legacy TrackerRepository during the migration
period. Once migration is complete, this repository should be the primary interface
for workout event operations.
"""

from typing import Sequence, TypeVar, Type
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from infrastructure.database.models.workout_event import (
    WorkoutEvent,
    RoutineCompletedEvent,
    ExercisePlanStartedEvent,
    ExercisePlanCompletedEvent,
)
from infrastructure.database.repositories.base_repository import BaseRepository


# Type variable for polymorphic event types
T = TypeVar("T", bound=WorkoutEvent)


class WorkoutEventRepository(BaseRepository[WorkoutEvent, dict, dict]):
    """
    Repository for WorkoutEvent entity operations.

    Provides type-safe methods for recording and querying workout events,
    with specialized methods for each event type (routine completion,
    exercise plan start/end).

    This repository uses SQLAlchemy's polymorphic query capabilities to
    return the correct Python class for each event type.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize the WorkoutEvent repository.

        Args:
            db: The database session
        """
        super().__init__(WorkoutEvent, db)

    # =====================================================================
    # Generic Event Methods
    # =====================================================================

    def get_by_id(self, event_id: int) -> WorkoutEvent | None:
        """
        Retrieve a workout event by its ID.

        SQLAlchemy automatically returns the correct polymorphic subclass.

        Args:
            event_id: The event's primary key

        Returns:
            The WorkoutEvent instance (or subclass) if found, None otherwise
        """
        return self.db.query(WorkoutEvent).filter(
            WorkoutEvent.event_id == event_id
        ).first()

    def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[WorkoutEvent]:
        """
        Retrieve all workout events for a user with pagination.

        Args:
            user_id: The user's ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of WorkoutEvent instances (and subclasses)
        """
        return self.db.query(WorkoutEvent).filter(
            WorkoutEvent.user_id == user_id
        ).order_by(
            WorkoutEvent.timestamp.desc()
        ).offset(skip).limit(limit).all()

    def get_events_by_type(
        self,
        event_class: Type[T],
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[T]:
        """
        Retrieve events of a specific type for a user.

        This is a generic method that works with any WorkoutEvent subclass.

        Args:
            event_class: The specific event class to query
            user_id: The user's ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of events of the specified type
        """
        return self.db.query(event_class).filter(
            event_class.user_id == user_id
        ).order_by(
            event_class.timestamp.desc()
        ).offset(skip).limit(limit).all()

    def get_latest_by_type(
        self,
        event_class: Type[T],
        user_id: int
    ) -> T | None:
        """
        Get the most recent event of a specific type for a user.

        Args:
            event_class: The specific event class to query
            user_id: The user's ID

        Returns:
            The most recent event of the specified type, or None
        """
        return self.db.query(event_class).filter(
            event_class.user_id == user_id
        ).order_by(
            event_class.timestamp.desc()
        ).first()

    # =====================================================================
    # Routine Completed Event Methods
    # =====================================================================

    def record_routine_completed(
        self,
        user_id: int,
        routine_group: str,
        exercise_increments: dict | None = None,
        push_increment: int = 0,
        pull_increment: int = 0,
        isometric_increment: int = 0,
        push_time_increment: int = 0,
        pull_time_increment: int = 0,
        isometric_time_increment: int = 0
    ) -> RoutineCompletedEvent:
        """
        Record a routine completion event.

        Args:
            user_id: The user's ID
            routine_group: The routine group name (e.g., "push", "pull", "legs")
            exercise_increments: Dictionary of exercise-specific increments
            push_increment: Total push exercise increment
            pull_increment: Total pull exercise increment
            isometric_increment: Total isometric exercise increment
            push_time_increment: Total push time increment
            pull_time_increment: Total pull time increment
            isometric_time_increment: Total isometric time increment

        Returns:
            The created RoutineCompletedEvent
        """
        event = RoutineCompletedEvent(
            user_id=user_id,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            routine_group=routine_group,
            exercise_increments=exercise_increments,
            push_increment=push_increment,
            pull_increment=pull_increment,
            isometric_increment=isometric_increment,
            push_time_increment=push_time_increment,
            pull_time_increment=pull_time_increment,
            isometric_time_increment=isometric_time_increment
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def record_routine_completed_from_dict(
        self,
        user_id: int,
        data: dict
    ) -> RoutineCompletedEvent:
        """
        Record a routine completion event from dictionary data.

        This method provides compatibility with the legacy record format.

        Args:
            user_id: The user's ID
            data: Dictionary containing routine completion data

        Returns:
            The created RoutineCompletedEvent
        """
        # Map legacy field names to new field names
        routine_group = data.get("info_description") or data.get("routine_group")
        timestamp = data.get("record_datetime") or data.get("timestamp")

        if timestamp is None:
            timestamp = datetime.now(timezone.utc).replace(tzinfo=None)

        event = RoutineCompletedEvent(
            user_id=user_id,
            timestamp=timestamp,
            routine_group=routine_group,
            exercise_increments=data.get("exercise_increments"),
            push_increment=data.get("push_increment", 0),
            pull_increment=data.get("pull_increment", 0),
            isometric_increment=data.get("isometric_increment", 0),
            push_time_increment=data.get("push_time_increment", 0),
            pull_time_increment=data.get("pull_time_increment", 0),
            isometric_time_increment=data.get("isometric_time_increment", 0)
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_routine_completions(
        self,
        user_id: int,
        routine_group: str | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[RoutineCompletedEvent]:
        """
        Get routine completion events for a user.

        Args:
            user_id: The user's ID
            routine_group: Optional filter by routine group
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of RoutineCompletedEvent instances
        """
        query = self.db.query(RoutineCompletedEvent).filter(
            RoutineCompletedEvent.user_id == user_id
        )

        if routine_group:
            query = query.filter(
                RoutineCompletedEvent.routine_group == routine_group
            )

        return query.order_by(
            RoutineCompletedEvent.timestamp.desc()
        ).offset(skip).limit(limit).all()

    def get_last_routine_completion(
        self,
        user_id: int
    ) -> RoutineCompletedEvent | None:
        """
        Get the most recent routine completion for a user.

        Args:
            user_id: The user's ID

        Returns:
            The most recent RoutineCompletedEvent, or None
        """
        return self.get_latest_by_type(RoutineCompletedEvent, user_id)

    def count_routine_completions(self, user_id: int) -> int:
        """
        Count total routine completions for a user.

        Args:
            user_id: The user's ID

        Returns:
            Number of routine completions
        """
        return self.db.query(RoutineCompletedEvent).filter(
            RoutineCompletedEvent.user_id == user_id
        ).count()

    # =====================================================================
    # Exercise Plan Started Event Methods
    # =====================================================================

    def record_exercise_plan_started(
        self,
        user_id: int,
        exercise_plan_id: int
    ) -> ExercisePlanStartedEvent:
        """
        Record an exercise plan start event.

        Args:
            user_id: The user's ID
            exercise_plan_id: The exercise plan ID being started

        Returns:
            The created ExercisePlanStartedEvent
        """
        event = ExercisePlanStartedEvent(
            user_id=user_id,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            exercise_plan_id=exercise_plan_id
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_last_exercise_plan_start(
        self,
        user_id: int
    ) -> ExercisePlanStartedEvent | None:
        """
        Get the most recent exercise plan start for a user.

        Args:
            user_id: The user's ID

        Returns:
            The most recent ExercisePlanStartedEvent, or None
        """
        return self.get_latest_by_type(ExercisePlanStartedEvent, user_id)

    # =====================================================================
    # Exercise Plan Completed Event Methods
    # =====================================================================

    def record_exercise_plan_completed(
        self,
        user_id: int,
        exercise_plan_id: int
    ) -> ExercisePlanCompletedEvent:
        """
        Record an exercise plan completion event.

        Args:
            user_id: The user's ID
            exercise_plan_id: The exercise plan ID being completed

        Returns:
            The created ExercisePlanCompletedEvent
        """
        event = ExercisePlanCompletedEvent(
            user_id=user_id,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            exercise_plan_id=exercise_plan_id
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_last_exercise_plan_completion(
        self,
        user_id: int
    ) -> ExercisePlanCompletedEvent | None:
        """
        Get the most recent exercise plan completion for a user.

        Args:
            user_id: The user's ID

        Returns:
            The most recent ExercisePlanCompletedEvent, or None
        """
        return self.get_latest_by_type(ExercisePlanCompletedEvent, user_id)

    def count_exercise_plan_completions(self, user_id: int) -> int:
        """
        Count total exercise plan completions for a user.

        Args:
            user_id: The user's ID

        Returns:
            Number of exercise plan completions
        """
        return self.db.query(ExercisePlanCompletedEvent).filter(
            ExercisePlanCompletedEvent.user_id == user_id
        ).count()

    # =====================================================================
    # Statistics Methods
    # =====================================================================

    def get_total_increments(self, user_id: int) -> dict:
        """
        Calculate total exercise increments for a user.

        Args:
            user_id: The user's ID

        Returns:
            Dictionary with total increments by type
        """
        completions = self.get_routine_completions(user_id, limit=10000)

        totals = {
            "push_increment": 0,
            "pull_increment": 0,
            "isometric_increment": 0,
            "push_time_increment": 0,
            "pull_time_increment": 0,
            "isometric_time_increment": 0
        }

        for event in completions:
            totals["push_increment"] += event.push_increment or 0
            totals["pull_increment"] += event.pull_increment or 0
            totals["isometric_increment"] += event.isometric_increment or 0
            totals["push_time_increment"] += event.push_time_increment or 0
            totals["pull_time_increment"] += event.pull_time_increment or 0
            totals["isometric_time_increment"] += event.isometric_time_increment or 0

        return totals

    def get_user_statistics(self, user_id: int) -> dict:
        """
        Get comprehensive user statistics.

        Args:
            user_id: The user's ID

        Returns:
            Dictionary containing user workout statistics
        """
        totals = self.get_total_increments(user_id)

        return {
            "total_routines_completed": self.count_routine_completions(user_id),
            "total_exercise_plans_completed": self.count_exercise_plan_completions(user_id),
            "total_push_increment": totals["push_increment"],
            "total_pull_increment": totals["pull_increment"],
            "total_isometric_increment": totals["isometric_increment"],
            "total_push_time_increment": totals["push_time_increment"],
            "total_pull_time_increment": totals["pull_time_increment"],
            "total_isometric_time_increment": totals["isometric_time_increment"],
        }

    # =====================================================================
    # Cleanup Methods
    # =====================================================================

    def delete_by_user(self, user_id: int) -> int:
        """
        Delete all workout events for a user.

        Args:
            user_id: The user's ID

        Returns:
            Number of events deleted
        """
        result = self.db.query(WorkoutEvent).filter(
            WorkoutEvent.user_id == user_id
        ).delete()
        self.db.commit()
        return result
