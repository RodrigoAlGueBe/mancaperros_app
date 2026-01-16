"""
Routine Service Module

This module encapsulates all business logic related to routine operations,
including global routines, user routines, and routine completion tracking.
"""

import json
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from utils.functions import f_reps_to_seconds
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


class RoutineService:
    """
    Service class for handling routine-related business logic.

    This service encapsulates all routine operations including:
    - Creating global routines for exercise plans
    - Creating exercises for routines
    - Ending/completing routines and tracking progress
    - Getting assigned routines for users
    - Calculating next routines based on user history
    """

    def __init__(self, db: Session):
        """
        Initialize the RoutineService with a database session.

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

    def create_routine_global(
        self,
        user_email: str,
        routine_data: schemas.Rutine_global_Create
    ) -> models.Rutine_global:
        """
        Create a new global routine for an exercise plan.

        Business rules:
        - User must exist
        - Exercise plan must exist
        - Routine name must be unique within the exercise plan

        Args:
            user_email: The email of the user creating the routine
            routine_data: Schema containing routine details

        Returns:
            The created routine global model

        Raises:
            HTTPException: If validation fails
        """
        self._validate_user_exists(user_email)

        # Validate exercise plan exists using repository
        exercise_plan = self.exercise_plan_global_repo.get_by_id(routine_data.exercise_plan_id)
        if not exercise_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise plan not found"
            )

        # Check for duplicate routine name within the exercise plan using repository
        existing_routine = self.routine_global_repo.get_by_name_and_plan(
            routine_data.rutine_name, routine_data.exercise_plan_id
        )
        if existing_routine:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Routine name already exists for this exercise plan"
            )

        return self.routine_global_repo.create_from_schema(routine_data)

    def create_exercise_global(
        self,
        user_email: str,
        exercise_data: schemas.Exercise_global_Create
    ) -> models.Exercise_global:
        """
        Create a new global exercise for a routine.

        Business rules:
        - User must exist
        - Routine must exist
        - Exercise plan must exist
        - Exercise name must be unique within the routine

        Args:
            user_email: The email of the user creating the exercise
            exercise_data: Schema containing exercise details

        Returns:
            The created exercise global model

        Raises:
            HTTPException: If validation fails
        """
        self._validate_user_exists(user_email)

        # Validate routine exists using repository
        routine = self.routine_global_repo.get_by_id(exercise_data.rutine_id)
        if not routine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Routine not found"
            )

        # Validate exercise plan exists using repository
        exercise_plan = self.exercise_plan_global_repo.get_by_id(routine.exercise_plan_id)
        if not exercise_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise plan not found"
            )

        # Check for duplicate exercise name within the routine using repository
        existing_exercise = self.exercise_global_repo.get_by_name_in_routine(
            exercise_data.exercise_name, routine.rutine_id
        )
        if existing_exercise:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exercise name already exists for this Routine"
            )

        return self.exercise_global_repo.create_from_schema(exercise_data)

    def end_routine(
        self,
        user_email: str,
        exercises_summary: dict[str, Any]
    ) -> dict[str, str]:
        """
        End/complete a routine and record progress.

        This is the main business logic extracted from the original end_routine endpoint.
        It performs the following operations:
        1. Validates user and retrieves current exercise plan
        2. Gets the routine being completed
        3. Updates exercise repetitions based on user performance
        4. Calculates increments for different exercise types (push, pull, isometric)
        5. Records the routine completion in the tracker

        Business rules:
        - Number of exercises received must match the routine's exercises
        - Exercise increments are calculated based on type (push, pull, isometric)
        - Isometric exercises have their time converted to seconds for tracking

        Args:
            user_email: The email of the user completing the routine
            exercises_summary: Dictionary containing:
                - routine_group: The group identifier of the routine
                - exercises: Dictionary of exercises with their new rep values

        Returns:
            Dictionary with success message

        Raises:
            HTTPException: If user not found or routine mismatch
        """
        user = self._validate_user_exists(user_email)

        # Get the last/current exercise plan for the user using repository
        last_exercise_plan = self.exercise_plan_repo.get_by_user_id(user.user_id)

        if not last_exercise_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active exercise plan found for user"
            )

        # Get the routine being completed using repository
        last_routine = self.routine_repo.get_by_exercise_plan_and_group(
            last_exercise_plan.exercise_plan_id, exercises_summary["routine_group"]
        )

        if not last_routine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Routine not found for the given group"
            )

        # Get exercises from the summary
        exercises_received = exercises_summary["exercises"]
        exercise_quantity = len(exercises_received)

        # Validate exercise count matches
        if exercise_quantity != len(last_routine.exercises):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Received routine does not match with started routine"
            )

        # Initialize exercise record for tracking
        exercise_record = {
            "record_datetime": datetime.now(timezone.utc).replace(tzinfo=None),
            "info_type": "rutine_end",
            "info_description": exercises_summary["routine_group"],
            "exercise_increments": {},
            "push_increment": 0,
            "pull_increment": 0,
            "isometric_increment": 0,
        }

        # Process each exercise
        exercise_order_name = "exercise_"
        exercise_sequence = "start"

        for exercise_db in last_routine.exercises:
            # Get the new reps from the received data
            new_reps = exercises_received[
                exercise_order_name + str(exercise_sequence)
            ]["reps"]

            # Calculate increment (difference between old and new reps)
            exercise_record["exercise_increments"][exercise_db.exercise_name] = (
                int(exercise_db.rep) - int(new_reps)
            )

            # Update the exercise with new reps
            exercise_db.rep = new_reps

            # Determine exercise type and update increments accordingly
            exercise_type = exercise_db.exercise_type.split('-')

            if exercise_type[0] == "push":
                exercise_record["push_increment"] += (
                    int(exercise_db.rep) - int(new_reps)
                )
            elif exercise_type[0] == "pull":
                exercise_record["pull_increment"] += (
                    int(exercise_db.rep) - int(new_reps)
                )
            else:
                # Isometric exercises - convert to seconds for tracking
                exercise_record["isometric_increment"] += (
                    int(f_reps_to_seconds(exercise_db.rep)) -
                    int(f_reps_to_seconds(new_reps))
                )

            # Update exercise sequence for next iteration
            if exercise_sequence == "start":
                exercise_sequence = 2
            elif exercise_sequence == "end":
                break
            elif int(exercise_sequence) < exercise_quantity - 1:
                exercise_sequence += 1
            else:
                exercise_sequence = "end"

        # Update the routine in the database using repository
        self.routine_repo.update(last_routine)

        # Record the routine completion using repository
        self.tracker_repo.record_routine_end_from_dict(user.user_id, exercise_record)

        return {"detail": "Routine ended correctly"}

    def get_assigned_routines(self, user_email: str) -> list[models.Rutine]:
        """
        Get all routines assigned to a user through their exercise plan.

        Args:
            user_email: The email of the user

        Returns:
            List of routine models assigned to the user

        Raises:
            HTTPException: If user not found
        """
        user = self._validate_user_exists(user_email)

        # Get the user's current exercise plan using repository
        assigned_exercise_plan = self.exercise_plan_repo.get_by_user_id(user.user_id)

        if not assigned_exercise_plan:
            return []

        return self.routine_repo.get_by_exercise_plan_id(assigned_exercise_plan.exercise_plan_id)

    def get_routines_for_exercise_plan(
        self,
        exercise_plan_id: int
    ) -> list[models.Rutine]:
        """
        Get all routines for a specific exercise plan.

        Args:
            exercise_plan_id: The exercise plan ID

        Returns:
            List of routine models for the exercise plan
        """
        return self.routine_repo.get_by_exercise_plan_id(exercise_plan_id)

    def get_exercises_for_routine(
        self,
        routine_id: int
    ) -> dict[str, Any]:
        """
        Get all exercises for a specific routine with formatted output.

        Args:
            routine_id: The routine ID

        Returns:
            Dictionary containing routine info and formatted exercises

        Raises:
            HTTPException: If routine not found
        """
        routine = self.routine_repo.get_by_id(routine_id)

        if not routine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rutine not found"
            )

        exercises = self.exercise_repo.get_by_routine_id(routine_id)

        output_response = {
            "routine_group": routine.rutine_group,
            "rutine_type": routine.rutine_type,
            "rutine_category": routine.rutine_category,
            "num_series": routine.rounds,
            "rest_between_exercises": routine.rst_btw_exercises,
            "rest_between_series": routine.rst_btw_rounds,
            "exercises": {}
        }

        count = 0
        for exercise in exercises:
            count += 1
            exercise_data = {
                "exercise_name": exercise.exercise_name,
                "image": exercise.image,
                "reps": exercise.rep,
                "exercise_type": exercise.exercise_type,
                "exercise_group": exercise.exercise_group
            }

            if len(output_response["exercises"]) == 0:
                output_response["exercises"]["exercise_start"] = exercise_data
            elif len(output_response["exercises"]) == len(exercises) - 1:
                output_response["exercises"]["exercise_end"] = exercise_data
            else:
                output_response["exercises"][f"exercise_{count}"] = exercise_data

        return output_response

    def get_next_routine(self, user_email: str) -> dict[str, Any]:
        """
        Calculate and return the next routine for a user.

        This method determines which routine the user should do next based on:
        1. The routine group order defined in the exercise plan
        2. The last completed routine from the user's tracker

        Business rules:
        - If the user just started the exercise plan, return the first routine
        - Otherwise, find the next routine in the sequence
        - If at the end of the sequence, loop back to the beginning

        Args:
            user_email: The email of the user

        Returns:
            Dictionary containing:
                - routine: The routine group name
                - routine_id: The routine ID

        Raises:
            HTTPException: If user or active exercise plan not found
        """
        user = self._validate_user_exists(user_email)

        # Get active exercise plan using repository
        active_exercise_plan = self.exercise_plan_repo.get_by_user_id(user.user_id)

        if not active_exercise_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active exercise plan found"
            )

        # Parse routine group order
        try:
            routine_order = json.loads(active_exercise_plan.routine_group_order)
        except (ValueError, TypeError):
            routine_order = active_exercise_plan.routine_group_order

        # Get the last completed routine using repository
        last_routine = self.tracker_repo.get_latest_by_user_and_type(user.user_id, "rutine_end")

        # Get the start time of the current exercise plan using repository
        exercise_plan_start = self.tracker_repo.get_latest_by_user_and_type(
            user.user_id, "exercise_plan_start"
        )

        # Determine next routine
        if (not last_routine or
            (exercise_plan_start and
             exercise_plan_start.record_datetime > last_routine.record_datetime)):
            # New exercise plan or no completed routines - start from beginning
            next_routine = routine_order[0] if routine_order else None
        else:
            # Find the next routine in the sequence
            last_routine_group = last_routine.info_description
            next_routine = None

            for i, muscular_group in enumerate(routine_order):
                if muscular_group == last_routine_group:
                    if i + 1 < len(routine_order):
                        next_routine = routine_order[i + 1]
                    else:
                        # Loop back to beginning
                        next_routine = routine_order[0]
                    break

        if not next_routine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not determine next routine"
            )

        # Get the routine ID using repository
        routine = self.routine_repo.get_by_exercise_plan_and_group(
            active_exercise_plan.exercise_plan_id, next_routine
        )

        if not routine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Routine not found in exercise plan"
            )

        return {
            'routine': next_routine,
            'routine_id': routine.rutine_id
        }


def get_routine_service(db: Session) -> RoutineService:
    """
    Factory function to create a RoutineService instance.

    This function can be used as a FastAPI dependency.

    Args:
        db: SQLAlchemy database session

    Returns:
        Configured RoutineService instance
    """
    return RoutineService(db)
