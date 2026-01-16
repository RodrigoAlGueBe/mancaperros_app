"""
User Tracker Repository implementation.

This module provides data access operations for User_Tracker entities,
encapsulating all tracking-related database queries.

MIGRATION NOTE:
---------------
This repository works with the legacy User_Tracker model (users_tracker table).
For new code, prefer using WorkoutEventRepository which works with the new
polymorphic WorkoutEvent model (workout_events table).

During the migration period, this repository can optionally write to both
tables for data consistency. Set use_dual_write=True in the constructor.
"""

from typing import Sequence
from datetime import datetime, timezone

from sqlalchemy.orm import Session

import models
import schemas
from infrastructure.database.repositories.base_repository import BaseRepository


class TrackerRepository(BaseRepository[models.User_Tracker, dict, dict]):
    """
    Repository for User_Tracker entity operations (LEGACY).

    Provides methods for tracking user activities like exercise plan
    starts, ends, and routine completions.

    DEPRECATION NOTICE:
    This repository is maintained for backward compatibility with the
    legacy users_tracker table. For new features, use WorkoutEventRepository
    with the new polymorphic event models.

    The dual_write mode allows writing to both legacy and new tables
    during migration.
    """

    def __init__(self, db: Session, use_dual_write: bool = False) -> None:
        """
        Initialize the Tracker repository.

        Args:
            db: The database session
            use_dual_write: If True, writes will also be recorded in the
                           new workout_events table for migration purposes
        """
        super().__init__(models.User_Tracker, db)
        self._use_dual_write = use_dual_write
        self._workout_event_repo = None

    @property
    def workout_event_repo(self):
        """Lazy initialization of WorkoutEventRepository for dual-write mode."""
        if self._workout_event_repo is None and self._use_dual_write:
            from infrastructure.database.repositories.workout_event_repository import (
                WorkoutEventRepository
            )
            self._workout_event_repo = WorkoutEventRepository(self.db)
        return self._workout_event_repo

    def get_by_id(self, tracker_id: int) -> models.User_Tracker | None:
        """
        Retrieve a tracker record by its ID.

        Args:
            tracker_id: The tracker's primary key

        Returns:
            The User_Tracker instance if found, None otherwise
        """
        return self.db.query(models.User_Tracker).filter(
            models.User_Tracker.user_tracker_id == tracker_id
        ).first()

    def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[models.User_Tracker]:
        """
        Retrieve all tracker records for a user with pagination.

        Args:
            user_id: The user's ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of User_Tracker instances
        """
        return self.db.query(models.User_Tracker).filter(
            models.User_Tracker.user_id == user_id
        ).offset(skip).limit(limit).all()

    def get_by_user_and_type(
        self,
        user_id: int,
        info_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[models.User_Tracker]:
        """
        Retrieve tracker records by user and type with pagination.

        Args:
            user_id: The user's ID
            info_type: The type of tracking info
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of User_Tracker instances
        """
        return self.db.query(models.User_Tracker).filter(
            models.User_Tracker.user_id == user_id,
            models.User_Tracker.info_type == info_type
        ).offset(skip).limit(limit).all()

    def get_latest_by_type(
        self,
        user_id: int,
        info_type: str
    ) -> models.User_Tracker | None:
        """
        Get the most recent tracker record of a specific type for a user.

        Args:
            user_id: The user's ID
            info_type: The type of tracking info

        Returns:
            The most recent User_Tracker instance if found, None otherwise
        """
        return self.db.query(models.User_Tracker).filter(
            models.User_Tracker.user_id == user_id,
            models.User_Tracker.info_type == info_type
        ).order_by(models.User_Tracker.record_datetime.desc()).first()

    def get_last_routine_end(self, user_id: int) -> models.User_Tracker | None:
        """
        Get the most recent routine end record for a user.

        Args:
            user_id: The user's ID

        Returns:
            The most recent routine end tracker if found, None otherwise
        """
        return self.get_latest_by_type(user_id, "rutine_end")

    def get_last_exercise_plan_start(self, user_id: int) -> models.User_Tracker | None:
        """
        Get the most recent exercise plan start record for a user.

        Args:
            user_id: The user's ID

        Returns:
            The most recent exercise plan start tracker if found, None otherwise
        """
        return self.get_latest_by_type(user_id, "exercise_plan_start")

    def get_last_exercise_plan_end(self, user_id: int) -> models.User_Tracker | None:
        """
        Get the most recent exercise plan end record for a user.

        Args:
            user_id: The user's ID

        Returns:
            The most recent exercise plan end tracker if found, None otherwise
        """
        return self.get_latest_by_type(user_id, "exercise_plan_end")

    def record_exercise_plan_start(
        self,
        user_id: int,
        exercise_plan_id: int
    ) -> models.User_Tracker:
        """
        Record the start of an exercise plan.

        Args:
            user_id: The user's ID
            exercise_plan_id: The exercise plan ID being started

        Returns:
            The created User_Tracker instance

        Note:
            If dual_write is enabled, also creates an ExercisePlanStartedEvent
            in the new workout_events table.
        """
        db_record = models.User_Tracker(
            user_id=user_id,
            info_type="exercise_plan_start",
            info_description=str(exercise_plan_id),
            record_datetime=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)

        # Dual-write to new table if enabled
        if self._use_dual_write and self.workout_event_repo:
            self.workout_event_repo.record_exercise_plan_started(
                user_id=user_id,
                exercise_plan_id=exercise_plan_id
            )

        return db_record

    def record_exercise_plan_end(
        self,
        user_id: int,
        exercise_plan_id: int
    ) -> models.User_Tracker:
        """
        Record the end of an exercise plan.

        Args:
            user_id: The user's ID
            exercise_plan_id: The exercise plan ID being ended

        Returns:
            The created User_Tracker instance

        Note:
            If dual_write is enabled, also creates an ExercisePlanCompletedEvent
            in the new workout_events table.
        """
        db_record = models.User_Tracker(
            user_id=user_id,
            info_type="exercise_plan_end",
            info_description=str(exercise_plan_id),
            record_datetime=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)

        # Dual-write to new table if enabled
        if self._use_dual_write and self.workout_event_repo:
            self.workout_event_repo.record_exercise_plan_completed(
                user_id=user_id,
                exercise_plan_id=exercise_plan_id
            )

        return db_record

    def record_routine_end(
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
    ) -> models.User_Tracker:
        """
        Record the end of a routine with exercise data.

        Args:
            user_id: The user's ID
            routine_group: The routine group name
            exercise_increments: Dictionary of exercise increments
            push_increment: Total push increment
            pull_increment: Total pull increment
            isometric_increment: Total isometric increment
            push_time_increment: Total push time increment
            pull_time_increment: Total pull time increment
            isometric_time_increment: Total isometric time increment

        Returns:
            The created User_Tracker instance

        Note:
            If dual_write is enabled, also creates a RoutineCompletedEvent
            in the new workout_events table.
        """
        db_record = models.User_Tracker(
            user_id=user_id,
            record_datetime=datetime.now(timezone.utc).replace(tzinfo=None),
            info_type="rutine_end",
            info_description=routine_group,
            exercise_increments=exercise_increments,
            push_increment=push_increment,
            pull_increment=pull_increment,
            isometric_increment=isometric_increment,
            push_time_increment=push_time_increment,
            pull_time_increment=pull_time_increment,
            isometric_time_increment=isometric_time_increment
        )
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)

        # Dual-write to new table if enabled
        if self._use_dual_write and self.workout_event_repo:
            self.workout_event_repo.record_routine_completed(
                user_id=user_id,
                routine_group=routine_group,
                exercise_increments=exercise_increments,
                push_increment=push_increment,
                pull_increment=pull_increment,
                isometric_increment=isometric_increment,
                push_time_increment=push_time_increment,
                pull_time_increment=pull_time_increment,
                isometric_time_increment=isometric_time_increment
            )

        return db_record

    def record_routine_end_from_dict(
        self,
        user_id: int,
        exercise_record: dict
    ) -> models.User_Tracker:
        """
        Record the end of a routine from dictionary data.

        Args:
            user_id: The user's ID
            exercise_record: Dictionary with routine end data

        Returns:
            The created User_Tracker instance

        Note:
            If dual_write is enabled, also creates a RoutineCompletedEvent
            in the new workout_events table.
        """
        db_record = models.User_Tracker(
            **exercise_record,
            user_id=user_id
        )
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)

        # Dual-write to new table if enabled
        if self._use_dual_write and self.workout_event_repo:
            self.workout_event_repo.record_routine_completed_from_dict(
                user_id=user_id,
                data=exercise_record
            )

        return db_record

    def get_user_history(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[models.User_Tracker]:
        """
        Get user's tracking history with pagination.

        Args:
            user_id: The user's ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of User_Tracker instances ordered by date descending
        """
        return self.db.query(models.User_Tracker).filter(
            models.User_Tracker.user_id == user_id
        ).order_by(
            models.User_Tracker.record_datetime.desc()
        ).offset(skip).limit(limit).all()

    def get_routine_history(
        self,
        user_id: int,
        routine_group: str | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[models.User_Tracker]:
        """
        Get user's routine completion history.

        Args:
            user_id: The user's ID
            routine_group: Optional filter by routine group
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of routine end User_Tracker instances
        """
        query = self.db.query(models.User_Tracker).filter(
            models.User_Tracker.user_id == user_id,
            models.User_Tracker.info_type == "rutine_end"
        )

        if routine_group:
            query = query.filter(
                models.User_Tracker.info_description == routine_group
            )

        return query.order_by(
            models.User_Tracker.record_datetime.desc()
        ).offset(skip).limit(limit).all()

    def get_total_increments(self, user_id: int) -> dict:
        """
        Calculate total exercise increments for a user.

        Args:
            user_id: The user's ID

        Returns:
            Dictionary with total increments by type
        """
        records = self.get_by_user_and_type(user_id, "rutine_end")

        totals = {
            "push_increment": 0,
            "pull_increment": 0,
            "isometric_increment": 0,
            "push_time_increment": 0,
            "pull_time_increment": 0,
            "isometric_time_increment": 0
        }

        for record in records:
            totals["push_increment"] += record.push_increment or 0
            totals["pull_increment"] += record.pull_increment or 0
            totals["isometric_increment"] += record.isometric_increment or 0
            totals["push_time_increment"] += record.push_time_increment or 0
            totals["pull_time_increment"] += record.pull_time_increment or 0
            totals["isometric_time_increment"] += record.isometric_time_increment or 0

        return totals

    def delete_by_user(self, user_id: int) -> int:
        """
        Delete all tracker records for a user.

        Args:
            user_id: The user's ID

        Returns:
            Number of records deleted
        """
        result = self.db.query(models.User_Tracker).filter(
            models.User_Tracker.user_id == user_id
        ).delete()
        self.db.commit()
        return result

    def count_routines_completed(self, user_id: int) -> int:
        """
        Count total routines completed by a user.

        Args:
            user_id: The user's ID

        Returns:
            Number of routines completed
        """
        return self.db.query(models.User_Tracker).filter(
            models.User_Tracker.user_id == user_id,
            models.User_Tracker.info_type == "rutine_end"
        ).count()

    def count_exercise_plans_completed(self, user_id: int) -> int:
        """
        Count total exercise plans completed by a user.

        Args:
            user_id: The user's ID

        Returns:
            Number of exercise plans completed
        """
        return self.db.query(models.User_Tracker).filter(
            models.User_Tracker.user_id == user_id,
            models.User_Tracker.info_type == "exercise_plan_end"
        ).count()

    def get_user_statistics(self, user_id: int) -> dict:
        """
        Get comprehensive user statistics from the legacy tracker.

        This method provides the same interface as WorkoutEventRepository
        for easier migration.

        Args:
            user_id: The user's ID

        Returns:
            Dictionary containing user workout statistics
        """
        totals = self.get_total_increments(user_id)

        return {
            "total_routines_completed": self.count_routines_completed(user_id),
            "total_exercise_plans_completed": self.count_exercise_plans_completed(user_id),
            "total_push_increment": totals["push_increment"],
            "total_pull_increment": totals["pull_increment"],
            "total_isometric_increment": totals["isometric_increment"],
            "total_push_time_increment": totals["push_time_increment"],
            "total_pull_time_increment": totals["pull_time_increment"],
            "total_isometric_time_increment": totals["isometric_time_increment"],
        }

    def get_latest_by_user_and_type(
        self,
        user_id: int,
        info_type: str
    ) -> models.User_Tracker | None:
        """
        Get the most recent record of a specific type for a user.

        Alias for get_latest_by_type for API consistency.

        Args:
            user_id: The user's ID
            info_type: The type of tracking info

        Returns:
            The most recent User_Tracker instance if found, None otherwise
        """
        return self.get_latest_by_type(user_id, info_type)
