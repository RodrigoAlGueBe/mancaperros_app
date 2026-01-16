"""
Exercise Plan Service Module

This module encapsulates all business logic related to exercise plan operations,
including global exercise plans and user-assigned exercise plans.
"""

from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from app.infrastructure.database.repositories import (
    UserRepository,
    ExercisePlanRepository,
    ExercisePlanGlobalRepository,
    RoutineRepository,
    RoutineGlobalRepository,
    ExerciseRepository,
    ExerciseGlobalRepository,
    TrackerRepository,
)


class ExercisePlanService:
    """
    Service class for handling exercise plan-related business logic.

    This service encapsulates all exercise plan operations including:
    - Creating global exercise plans
    - Creating complete exercise plans with routines and exercises
    - Assigning exercise plans to users
    - Retrieving available exercise plans
    - Managing exercise plan lifecycle
    """

    def __init__(self, db: Session):
        """
        Initialize the ExercisePlanService with a database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.user_repo = UserRepository(db)
        self.exercise_plan_repo = ExercisePlanRepository(db)
        self.exercise_plan_global_repo = ExercisePlanGlobalRepository(db)
        self.routine_repo = RoutineRepository(db)
        self.routine_global_repo = RoutineGlobalRepository(db)
        self.exercise_repo = ExerciseRepository(db)
        self.exercise_global_repo = ExerciseGlobalRepository(db)
        self.tracker_repo = TrackerRepository(db)

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

    def create_exercise_plan_global(
        self,
        user_email: str,
        exercise_plan_data: schemas.Exercise_plan_global_Create
    ) -> models.Exercise_plan_global:
        """
        Create a new global exercise plan.

        Business rules:
        - User must exist
        - Exercise plan name must be unique

        Args:
            user_email: The email of the user creating the plan
            exercise_plan_data: Schema containing exercise plan details

        Returns:
            The created exercise plan global model

        Raises:
            HTTPException: If user not found or plan name already exists
        """
        user = self._validate_user_exists(user_email)

        # Check for duplicate exercise plan name using repository
        if self.exercise_plan_global_repo.exists_by_name(exercise_plan_data.exercise_plan_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exercise plan already exists"
            )

        return self.exercise_plan_global_repo.create_from_schema(
            exercise_plan_data,
            user.user_id
        )

    def create_exercise_plan_global_full(
        self,
        user_email: str,
        exercise_plan_full_dict: dict[str, Any]
    ) -> dict[str, str]:
        """
        Create a complete exercise plan with all routines and exercises.

        This method creates an exercise plan along with all its associated
        routines and exercises in a single transaction.

        Args:
            user_email: The email of the user creating the plan
            exercise_plan_full_dict: Dictionary containing the complete plan structure:
                - exercise_plan_name: Name of the plan
                - exercise_plan_type: Type of exercise plan
                - difficult_level: Difficulty level
                - rutines: List of routines with their exercises

        Returns:
            Dictionary with success message

        Raises:
            HTTPException: If user not found or validation fails
        """
        user = self._validate_user_exists(user_email)

        # Create the global exercise plan using repository
        exercise_plan_global = self.exercise_plan_global_repo.create(
            exercise_plan_name=exercise_plan_full_dict['exercise_plan_name'],
            user_creator_id=user.user_id,
            exercise_plan_type=exercise_plan_full_dict['exercise_plan_type'],
            difficult_level=exercise_plan_full_dict['difficult_level'],
            routine_group_order=exercise_plan_full_dict.get('routine_group_order', [])
        )

        # Create routines and exercises using repositories
        for rutine in exercise_plan_full_dict['rutines']:
            rutine_global = self.routine_global_repo.create(
                rutine_name=rutine['rutine_name'],
                rutine_type=exercise_plan_global.exercise_plan_type,
                rutine_group=rutine['rutine_group'],
                rutine_category=rutine['rutine_category'],
                exercise_plan_id=exercise_plan_global.exercise_plan_id,
                rst_btw_exercises=rutine['rst_btw_exercises'],
                rst_btw_rounds=rutine['rst_btw_rounds'],
                difficult_level=rutine['difficult_level'],
                rounds=rutine['rounds'],
            )

            for exercise in rutine['exercises']:
                self.exercise_global_repo.create(
                    exercise_name=exercise['exercise_name'],
                    rep=exercise['rep'],
                    exercise_type=exercise['exercise_type'],
                    exercise_group=rutine_global.rutine_group,
                    rutine_id=rutine_global.rutine_id,
                    image=exercise['image']
                )

        return {"detail": "Entire exercise plan created correctly"}

    def assign_exercise_plan_to_user(
        self,
        user_email: str,
        exercise_plan_info: schemas.Exercise_plan_global_info
    ) -> dict[str, Any]:
        """
        Assign a global exercise plan to a user.

        Business rules:
        - If user already has an exercise plan, the old one is deleted and recorded
        - The global exercise plan is copied to create a user-specific instance
        - Start of the new exercise plan is recorded in the tracker

        Args:
            user_email: The email of the user
            exercise_plan_info: Schema containing exercise plan ID

        Returns:
            Dictionary with tracker information

        Raises:
            HTTPException: If user or exercise plan not found
        """
        user = self._validate_user_exists(user_email)

        # Get the global exercise plan with routines loaded using repository
        exercise_plan_global = self.exercise_plan_global_repo.get_by_id_with_routines(
            exercise_plan_info.exercise_plan_id
        )

        if not exercise_plan_global:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exercise plan not found"
            )

        # Handle existing exercise plan for user using repository
        if self.exercise_plan_repo.exists_for_user(user.user_id):
            # Record the end of the current exercise plan
            self.tracker_repo.record_exercise_plan_end(
                user.user_id,
                exercise_plan_global.exercise_plan_id
            )
            # Delete the existing exercise plan
            self.exercise_plan_repo.delete_for_user(user.user_id)

        # Assign the exercise plan to the user using repository
        self.exercise_plan_repo.assign_from_global(exercise_plan_global, user.user_id)

        # Record the start of the new exercise plan using repository
        tracker_record = self.tracker_repo.record_exercise_plan_start(
            user.user_id,
            exercise_plan_global.exercise_plan_id
        )

        return {
            "user_id": tracker_record.user_id,
            "user_tracker_id": tracker_record.user_tracker_id,
            "info_type": tracker_record.info_type,
            "record_datetime": tracker_record.record_datetime
        }

    def get_available_exercise_plans(
        self,
        exercise_plan_type: str
    ) -> list[models.Exercise_plan_global]:
        """
        Get all available exercise plans of a specific type.

        Args:
            exercise_plan_type: The type of exercise plans to retrieve

        Returns:
            List of exercise plan global models

        Raises:
            HTTPException: If no exercise plans are found
        """
        exercise_plans = self.exercise_plan_global_repo.get_by_type(exercise_plan_type)

        if not exercise_plans:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No exercise plans found"
            )

        return exercise_plans

    def get_user_exercise_plans(
        self,
        user_id: int
    ) -> list[models.Exercise_plan]:
        """
        Get all exercise plans assigned to a specific user.

        Args:
            user_id: The user's ID

        Returns:
            List of exercise plan models assigned to the user
        """
        return self.exercise_plan_repo.get_all_by_user_id(user_id)

    def get_exercise_plan_muscular_groups(
        self,
        user_email: str
    ) -> list[dict[str, Any]]:
        """
        Get the muscular groups (routine groups) for a user's exercise plan.

        Args:
            user_email: The email of the user

        Returns:
            List of dictionaries containing routine group and ID

        Raises:
            HTTPException: If user not found
        """
        user = self._validate_user_exists(user_email)

        exercise_plan = self.exercise_plan_repo.get_by_user_id(user.user_id)

        if not exercise_plan:
            return []

        return self.routine_repo.get_routine_groups_by_exercise_plan(
            exercise_plan.exercise_plan_id
        )


def get_exercise_plan_service(db: Session) -> ExercisePlanService:
    """
    Factory function to create an ExercisePlanService instance.

    This function can be used as a FastAPI dependency.

    Args:
        db: SQLAlchemy database session

    Returns:
        Configured ExercisePlanService instance
    """
    return ExercisePlanService(db)
