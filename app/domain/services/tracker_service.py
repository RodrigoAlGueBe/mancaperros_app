"""
Tracker Service Module

This module encapsulates all business logic related to user tracking operations,
including recording exercise plan starts/ends and routine completions.

HIGH-08 MIGRATION NOTE:
-----------------------
This service supports both the legacy User_Tracker model and the new
WorkoutEvent polymorphic model. During the transition period, operations
can write to both tables using dual-write mode.

Set use_new_models=True to prefer the new WorkoutEvent models for reads.
The legacy TrackerRepository will continue to work for backward compatibility.
"""

from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import models
from app.infrastructure.database.repositories import (
    UserRepository,
    ExercisePlanRepository,
    TrackerRepository,
)
from infrastructure.database.repositories.workout_event_repository import (
    WorkoutEventRepository,
)


class TrackerService:
    """
    Service class for handling user tracking-related business logic.

    This service encapsulates all tracker operations including:
    - Recording exercise plan lifecycle events (start/end)
    - Recording routine completion events
    - Retrieving tracker history and statistics
    - Analyzing user progress over time

    HIGH-08 MIGRATION:
    The service now supports dual-write mode and can optionally prefer
    the new WorkoutEvent models for read operations.
    """

    def __init__(
        self,
        db: Session,
        use_new_models: bool = False,
        use_dual_write: bool = True
    ):
        """
        Initialize the TrackerService with a database session.

        Args:
            db: SQLAlchemy database session
            use_new_models: If True, prefer new WorkoutEvent models for reads
            use_dual_write: If True, write to both legacy and new tables
        """
        self.db = db
        self.user_repo = UserRepository(db)
        self.exercise_plan_repo = ExercisePlanRepository(db)
        self.tracker_repo = TrackerRepository(db, use_dual_write=use_dual_write)
        self._use_new_models = use_new_models
        self._workout_event_repo = None

    @property
    def workout_event_repo(self) -> WorkoutEventRepository:
        """Lazy initialization of WorkoutEventRepository."""
        if self._workout_event_repo is None:
            self._workout_event_repo = WorkoutEventRepository(self.db)
        return self._workout_event_repo

    def _validate_user_exists(self, user_email: str) -> models.User:
        """
        Validate that a user exists by email.

        Args:
            user_email: The user's email address

        Returns:
            The user model if found

        Raises:
            HTTPException: If user is not found
        """
        user = self.user_repo.get_by_email(user_email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found"
            )
        return user

    def _get_user_by_id(self, user_id: int) -> models.User:
        """
        Get a user by ID.

        Args:
            user_id: The user's ID

        Returns:
            The user model if found

        Raises:
            HTTPException: If user is not found
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found"
            )
        return user

    def record_exercise_plan_start(
        self,
        user_id: int,
        exercise_plan_id: int
    ) -> models.User_Tracker | models.ExercisePlanStartedEvent:
        """
        Record the start of an exercise plan for a user.

        Args:
            user_id: The user's ID
            exercise_plan_id: The exercise plan ID being started

        Returns:
            The created tracker record (legacy or new model based on config)
        """
        # Legacy write (with dual-write if enabled)
        legacy_record = self.tracker_repo.record_exercise_plan_start(
            user_id, exercise_plan_id
        )

        if self._use_new_models:
            # Return new model if preferring new models
            return self.workout_event_repo.get_last_exercise_plan_start(user_id)

        return legacy_record

    def record_exercise_plan_end(
        self,
        user_id: int,
        exercise_plan_id: int
    ) -> models.User_Tracker | models.ExercisePlanCompletedEvent:
        """
        Record the end of an exercise plan for a user.

        Args:
            user_id: The user's ID
            exercise_plan_id: The exercise plan ID being ended

        Returns:
            The created tracker record (legacy or new model based on config)
        """
        # Legacy write (with dual-write if enabled)
        legacy_record = self.tracker_repo.record_exercise_plan_end(
            user_id, exercise_plan_id
        )

        if self._use_new_models:
            # Return new model if preferring new models
            return self.workout_event_repo.get_last_exercise_plan_completion(user_id)

        return legacy_record

    def record_routine_end(
        self,
        user_id: int,
        exercise_record: dict[str, Any]
    ) -> models.User_Tracker | models.RoutineCompletedEvent:
        """
        Record the completion of a routine.

        Args:
            user_id: The user's ID
            exercise_record: Dictionary containing routine completion data:
                - record_datetime: When the routine was completed
                - info_type: Type of record (should be "rutine_end")
                - info_description: Routine group identifier
                - exercise_increments: Dictionary of exercise name to increment
                - push_increment: Total push exercise increment
                - pull_increment: Total pull exercise increment
                - isometric_increment: Total isometric exercise increment

        Returns:
            The created tracker record (legacy or new model based on config)
        """
        # Legacy write (with dual-write if enabled)
        legacy_record = self.tracker_repo.record_routine_end_from_dict(
            user_id, exercise_record
        )

        if self._use_new_models:
            # Return new model if preferring new models
            return self.workout_event_repo.get_last_routine_completion(user_id)

        return legacy_record

    def get_user_tracker_history(
        self,
        user_email: str,
        info_type: str | None = None,
        limit: int = 100
    ) -> list:
        """
        Get the tracking history for a user.

        Args:
            user_email: The user's email
            info_type: Optional filter for specific event types
            limit: Maximum number of records to return

        Returns:
            List of tracker records ordered by datetime (newest first)

        Raises:
            HTTPException: If user not found
        """
        user = self._validate_user_exists(user_email)

        if self._use_new_models:
            # Use new WorkoutEvent models
            return list(self.workout_event_repo.get_by_user_id(
                user.user_id, skip=0, limit=limit
            ))

        # Legacy path
        if info_type:
            return list(self.tracker_repo.get_by_user_and_type(
                user.user_id, info_type, skip=0, limit=limit
            ))
        else:
            return list(self.tracker_repo.get_by_user_id(
                user.user_id, skip=0, limit=limit
            ))

    def get_last_completed_routine(
        self,
        user_email: str
    ) -> models.User_Tracker | models.RoutineCompletedEvent | None:
        """
        Get the last completed routine for a user.

        Args:
            user_email: The user's email

        Returns:
            The last routine completion record, or None if no routines completed

        Raises:
            HTTPException: If user not found
        """
        user = self._validate_user_exists(user_email)

        if self._use_new_models:
            return self.workout_event_repo.get_last_routine_completion(user.user_id)

        return self.tracker_repo.get_latest_by_user_and_type(user.user_id, "rutine_end")

    def get_exercise_plan_start_record(
        self,
        user_email: str
    ) -> models.User_Tracker | models.ExercisePlanStartedEvent | None:
        """
        Get the most recent exercise plan start record for a user.

        Args:
            user_email: The user's email

        Returns:
            The exercise plan start record, or None if none exists

        Raises:
            HTTPException: If user not found
        """
        user = self._validate_user_exists(user_email)

        if self._use_new_models:
            return self.workout_event_repo.get_last_exercise_plan_start(user.user_id)

        return self.tracker_repo.get_latest_by_user_and_type(
            user.user_id, "exercise_plan_start"
        )

    def get_user_progress_summary(
        self,
        user_email: str
    ) -> dict[str, Any]:
        """
        Get a summary of user's progress.

        This method aggregates tracking data to provide an overview of:
        - Total routines completed
        - Total push/pull/isometric increments
        - Current exercise plan info
        - Last workout date

        Args:
            user_email: The user's email

        Returns:
            Dictionary containing progress summary

        Raises:
            HTTPException: If user not found
        """
        user = self._validate_user_exists(user_email)

        if self._use_new_models:
            # Use new WorkoutEvent models
            stats = self.workout_event_repo.get_user_statistics(user.user_id)
            last_completion = self.workout_event_repo.get_last_routine_completion(
                user.user_id
            )
            last_workout = last_completion.timestamp if last_completion else None
        else:
            # Legacy path
            stats = self.tracker_repo.get_user_statistics(user.user_id)
            routine_history = self.tracker_repo.get_routine_history(
                user.user_id, limit=1
            )
            last_workout = (
                routine_history[0].record_datetime if routine_history else None
            )

        # Get current exercise plan using repository
        current_plan = self.exercise_plan_repo.get_by_user_id(user.user_id)

        return {
            "total_routines_completed": stats["total_routines_completed"],
            "total_push_increment": stats["total_push_increment"],
            "total_pull_increment": stats["total_pull_increment"],
            "total_isometric_increment": stats["total_isometric_increment"],
            "last_workout_date": last_workout,
            "current_exercise_plan": (
                current_plan.exercise_plan_name if current_plan else None
            ),
            "current_exercise_plan_id": (
                current_plan.exercise_plan_id if current_plan else None
            ),
        }

    def get_routine_completion_stats(
        self,
        user_email: str,
        routine_group: str | None = None
    ) -> dict[str, Any]:
        """
        Get statistics about routine completions.

        Args:
            user_email: The user's email
            routine_group: Optional filter for specific routine group

        Returns:
            Dictionary containing completion statistics

        Raises:
            HTTPException: If user not found
        """
        user = self._validate_user_exists(user_email)

        if self._use_new_models:
            # Use new WorkoutEvent models
            completions = self.workout_event_repo.get_routine_completions(
                user.user_id, routine_group=routine_group, limit=1000
            )
            # Group by routine group
            group_stats: dict[str, dict[str, Any]] = {}
            for completion in completions:
                group = completion.routine_group or "unknown"
                if group not in group_stats:
                    group_stats[group] = {
                        "count": 0,
                        "total_push": 0,
                        "total_pull": 0,
                        "total_isometric": 0,
                    }
                group_stats[group]["count"] += 1
                group_stats[group]["total_push"] += completion.push_increment or 0
                group_stats[group]["total_pull"] += completion.pull_increment or 0
                group_stats[group]["total_isometric"] += (
                    completion.isometric_increment or 0
                )
        else:
            # Legacy path
            completions = self.tracker_repo.get_routine_history(
                user.user_id, routine_group=routine_group, limit=1000
            )
            # Group by routine group
            group_stats = {}
            for completion in completions:
                group = completion.info_description or "unknown"
                if group not in group_stats:
                    group_stats[group] = {
                        "count": 0,
                        "total_push": 0,
                        "total_pull": 0,
                        "total_isometric": 0,
                    }
                group_stats[group]["count"] += 1
                group_stats[group]["total_push"] += completion.push_increment or 0
                group_stats[group]["total_pull"] += completion.pull_increment or 0
                group_stats[group]["total_isometric"] += (
                    completion.isometric_increment or 0
                )

        return {
            "total_completions": len(completions),
            "by_routine_group": group_stats,
        }

    def create_exercise_record(
        self,
        routine_group: str,
        exercise_increments: dict[str, int],
        push_increment: int = 0,
        pull_increment: int = 0,
        isometric_increment: int = 0
    ) -> dict[str, Any]:
        """
        Create an exercise record dictionary for routine completion tracking.

        This is a helper method to standardize the creation of exercise records
        that will be passed to record_routine_end.

        Args:
            routine_group: The routine group identifier
            exercise_increments: Dictionary mapping exercise names to their increments
            push_increment: Total push exercise increment
            pull_increment: Total pull exercise increment
            isometric_increment: Total isometric exercise increment

        Returns:
            Dictionary formatted for routine completion recording
        """
        return {
            "record_datetime": datetime.now(timezone.utc).replace(tzinfo=None),
            "info_type": "rutine_end",
            "info_description": routine_group,
            "exercise_increments": exercise_increments,
            "push_increment": push_increment,
            "pull_increment": pull_increment,
            "isometric_increment": isometric_increment,
        }


def get_tracker_service(
    db: Session,
    use_new_models: bool = False,
    use_dual_write: bool = True
) -> TrackerService:
    """
    Factory function to create a TrackerService instance.

    This function can be used as a FastAPI dependency.

    HIGH-08 MIGRATION:
    - use_new_models: Set to True to prefer new WorkoutEvent models for reads
    - use_dual_write: Set to True to write to both legacy and new tables

    Args:
        db: SQLAlchemy database session
        use_new_models: If True, prefer new WorkoutEvent models for reads
        use_dual_write: If True, write to both legacy and new tables

    Returns:
        Configured TrackerService instance
    """
    return TrackerService(
        db,
        use_new_models=use_new_models,
        use_dual_write=use_dual_write
    )


def get_tracker_service_new_models(db: Session) -> TrackerService:
    """
    Factory function to create a TrackerService using new models.

    Use this factory when you want to use the new WorkoutEvent models
    for both reads and writes.

    Args:
        db: SQLAlchemy database session

    Returns:
        TrackerService configured for new models
    """
    return TrackerService(db, use_new_models=True, use_dual_write=True)
