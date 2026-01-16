"""
Tracker Repository - Repository for User Tracker entity.

This module encapsulates all database operations related to the User_Tracker entity,
which tracks user activities like routine completions and exercise plan changes.
"""

from typing import Optional, List, Any, Dict
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import desc

from .base_repository import BaseRepository

# Import models
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
import models


class TrackerRepository(BaseRepository[models.User_Tracker, Any, Any]):
    """
    Repository for User_Tracker entity operations.

    Handles operations for tracking user activities including:
    - Exercise plan start/end events
    - Routine completion events
    - Exercise progress tracking
    """

    def __init__(self, db: Session):
        """
        Initialize the TrackerRepository.

        Args:
            db: The database session
        """
        super().__init__(models.User_Tracker, db)

    def get_by_id(self, tracker_id: int) -> Optional[models.User_Tracker]:
        """
        Retrieve a tracker record by its ID.

        Args:
            tracker_id: The tracker's primary key

        Returns:
            The User_Tracker if found, None otherwise
        """
        return self.db.query(models.User_Tracker).filter(
            models.User_Tracker.user_tracker_id == tracker_id
        ).first()

    def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.User_Tracker]:
        """
        Retrieve all tracker records for a specific user.

        Args:
            user_id: The user's ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of User_Tracker entities ordered by datetime (newest first)
        """
        return self.db.query(models.User_Tracker).filter(
            models.User_Tracker.user_id == user_id
        ).order_by(
            desc(models.User_Tracker.record_datetime)
        ).offset(skip).limit(limit).all()

    def get_by_user_and_type(
        self,
        user_id: int,
        info_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.User_Tracker]:
        """
        Retrieve tracker records for a user filtered by type.

        Args:
            user_id: The user's ID
            info_type: The type of tracking record (e.g., "rutine_end", "exercise_plan_start")
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of User_Tracker entities ordered by datetime (newest first)
        """
        return self.db.query(models.User_Tracker).filter(
            models.User_Tracker.user_id == user_id,
            models.User_Tracker.info_type == info_type
        ).order_by(
            desc(models.User_Tracker.record_datetime)
        ).offset(skip).limit(limit).all()

    def get_latest_by_user_and_type(
        self,
        user_id: int,
        info_type: str
    ) -> Optional[models.User_Tracker]:
        """
        Retrieve the most recent tracker record for a user of a specific type.

        Args:
            user_id: The user's ID
            info_type: The type of tracking record

        Returns:
            The most recent User_Tracker if found, None otherwise
        """
        return self.db.query(models.User_Tracker).filter(
            models.User_Tracker.user_id == user_id,
            models.User_Tracker.info_type == info_type
        ).order_by(
            desc(models.User_Tracker.record_datetime)
        ).first()

    def record_exercise_plan_start(
        self,
        user_id: int,
        exercise_plan_id: int
    ) -> models.User_Tracker:
        """
        Record the start of an exercise plan for a user.

        Args:
            user_id: The user's ID
            exercise_plan_id: The exercise plan's ID

        Returns:
            The created User_Tracker entity
        """
        db_tracker = models.User_Tracker(
            user_id=user_id,
            record_datetime=datetime.now(timezone.utc).replace(tzinfo=None),
            info_type="exercise_plan_start",
            info_description=str(exercise_plan_id)
        )
        self.db.add(db_tracker)
        self.db.commit()
        self.db.refresh(db_tracker)
        return db_tracker

    def record_exercise_plan_end(
        self,
        user_id: int,
        exercise_plan_id: int
    ) -> models.User_Tracker:
        """
        Record the end of an exercise plan for a user.

        Args:
            user_id: The user's ID
            exercise_plan_id: The exercise plan's ID

        Returns:
            The created User_Tracker entity
        """
        db_tracker = models.User_Tracker(
            user_id=user_id,
            record_datetime=datetime.now(timezone.utc).replace(tzinfo=None),
            info_type="exercise_plan_end",
            info_description=str(exercise_plan_id)
        )
        self.db.add(db_tracker)
        self.db.commit()
        self.db.refresh(db_tracker)
        return db_tracker

    def record_routine_end(
        self,
        user_id: int,
        routine_group: str,
        exercise_increments: Optional[Dict[str, int]] = None,
        push_increment: int = 0,
        pull_increment: int = 0,
        isometric_increment: int = 0,
        push_time_increment: int = 0,
        pull_time_increment: int = 0,
        isometric_time_increment: int = 0
    ) -> models.User_Tracker:
        """
        Record the completion of a routine.

        Args:
            user_id: The user's ID
            routine_group: The muscle group of the completed routine
            exercise_increments: Dictionary of exercise name to increment value
            push_increment: Total push exercise increment
            pull_increment: Total pull exercise increment
            isometric_increment: Total isometric exercise increment
            push_time_increment: Total push time increment
            pull_time_increment: Total pull time increment
            isometric_time_increment: Total isometric time increment

        Returns:
            The created User_Tracker entity
        """
        db_tracker = models.User_Tracker(
            user_id=user_id,
            record_datetime=datetime.now(timezone.utc).replace(tzinfo=None),
            info_type="rutine_end",
            info_description=routine_group,
            exercise_increments=exercise_increments or {},
            push_increment=push_increment,
            pull_increment=pull_increment,
            isometric_increment=isometric_increment,
            push_time_increment=push_time_increment,
            pull_time_increment=pull_time_increment,
            isometric_time_increment=isometric_time_increment
        )
        self.db.add(db_tracker)
        self.db.commit()
        self.db.refresh(db_tracker)
        return db_tracker

    def record_routine_end_from_dict(
        self,
        user_id: int,
        exercise_record: Dict[str, Any]
    ) -> models.User_Tracker:
        """
        Record the completion of a routine from a dictionary.

        Args:
            user_id: The user's ID
            exercise_record: Dictionary containing routine completion data

        Returns:
            The created User_Tracker entity
        """
        db_tracker = models.User_Tracker(
            **exercise_record,
            user_id=user_id
        )
        self.db.add(db_tracker)
        self.db.commit()
        self.db.refresh(db_tracker)
        return db_tracker

    def create(
        self,
        user_id: int,
        info_type: str,
        info_description: str = "Non_specifed",
        exercise_increments: Optional[Dict[str, int]] = None,
        push_increment: int = 0,
        pull_increment: int = 0,
        isometric_increment: int = 0,
        push_time_increment: int = 0,
        pull_time_increment: int = 0,
        isometric_time_increment: int = 0
    ) -> models.User_Tracker:
        """
        Create a new tracker record.

        Args:
            user_id: The user's ID
            info_type: Type of tracking record
            info_description: Description of the tracked event
            exercise_increments: Dictionary of exercise increments
            push_increment: Push exercise increment
            pull_increment: Pull exercise increment
            isometric_increment: Isometric exercise increment
            push_time_increment: Push time increment
            pull_time_increment: Pull time increment
            isometric_time_increment: Isometric time increment

        Returns:
            The created User_Tracker entity
        """
        db_tracker = models.User_Tracker(
            user_id=user_id,
            record_datetime=datetime.now(timezone.utc).replace(tzinfo=None),
            info_type=info_type,
            info_description=info_description,
            exercise_increments=exercise_increments,
            push_increment=push_increment,
            pull_increment=pull_increment,
            isometric_increment=isometric_increment,
            push_time_increment=push_time_increment,
            pull_time_increment=pull_time_increment,
            isometric_time_increment=isometric_time_increment
        )
        self.db.add(db_tracker)
        self.db.commit()
        self.db.refresh(db_tracker)
        return db_tracker

    def delete_by_user_id(self, user_id: int) -> int:
        """
        Delete all tracker records for a specific user.

        Args:
            user_id: The user's ID

        Returns:
            Number of deleted records
        """
        deleted_count = self.db.query(models.User_Tracker).filter(
            models.User_Tracker.user_id == user_id
        ).delete()
        self.db.commit()
        return deleted_count

    def get_routine_history(
        self,
        user_id: int,
        routine_group: Optional[str] = None,
        limit: int = 50
    ) -> List[models.User_Tracker]:
        """
        Get routine completion history for a user.

        Args:
            user_id: The user's ID
            routine_group: Optional filter by muscle group
            limit: Maximum number of records to return

        Returns:
            List of User_Tracker entities for routine completions
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
            desc(models.User_Tracker.record_datetime)
        ).limit(limit).all()

    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        Get aggregated statistics for a user.

        Args:
            user_id: The user's ID

        Returns:
            Dictionary containing user statistics
        """
        routine_completions = self.db.query(models.User_Tracker).filter(
            models.User_Tracker.user_id == user_id,
            models.User_Tracker.info_type == "rutine_end"
        ).all()

        total_push = sum(r.push_increment for r in routine_completions)
        total_pull = sum(r.pull_increment for r in routine_completions)
        total_isometric = sum(r.isometric_increment for r in routine_completions)

        return {
            "total_routines_completed": len(routine_completions),
            "total_push_increment": total_push,
            "total_pull_increment": total_pull,
            "total_isometric_increment": total_isometric
        }
