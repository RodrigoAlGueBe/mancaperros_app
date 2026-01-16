"""
Exercise Plan Repository implementation.

This module provides data access operations for Exercise_plan entities,
encapsulating all exercise plan-related database queries.
"""

from typing import Sequence
from datetime import datetime

from sqlalchemy.orm import Session, joinedload

import models
import schemas
from infrastructure.database.repositories.base_repository import BaseRepository


class ExercisePlanRepository(BaseRepository[models.Exercise_plan, schemas.Exercise_plan_Create, schemas.Exercise_plan_Base]):
    """
    Repository for Exercise_plan entity operations.

    Provides methods for exercise plan CRUD operations and
    specific domain queries.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize the Exercise Plan repository.

        Args:
            db: The database session
        """
        super().__init__(models.Exercise_plan, db)

    def get_by_id(self, exercise_plan_id: int) -> models.Exercise_plan | None:
        """
        Retrieve an exercise plan by its ID.

        Args:
            exercise_plan_id: The exercise plan's primary key

        Returns:
            The Exercise_plan instance if found, None otherwise
        """
        return self.db.query(models.Exercise_plan).filter(
            models.Exercise_plan.exercise_plan_id == exercise_plan_id
        ).first()

    def get_by_id_with_routines(self, exercise_plan_id: int) -> models.Exercise_plan | None:
        """
        Retrieve an exercise plan with its routines eagerly loaded.

        Args:
            exercise_plan_id: The exercise plan's primary key

        Returns:
            The Exercise_plan instance with routines if found, None otherwise
        """
        return self.db.query(models.Exercise_plan)\
            .options(joinedload(models.Exercise_plan.rutines))\
            .filter(models.Exercise_plan.exercise_plan_id == exercise_plan_id)\
            .first()

    def get_by_user_id(self, user_id: int) -> models.Exercise_plan | None:
        """
        Retrieve the exercise plan for a specific user.

        Args:
            user_id: The user's ID

        Returns:
            The Exercise_plan instance if found, None otherwise
        """
        return self.db.query(models.Exercise_plan).filter(
            models.Exercise_plan.user_owner_id == user_id
        ).first()

    def get_all_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[models.Exercise_plan]:
        """
        Retrieve all exercise plans for a specific user with pagination.

        Args:
            user_id: The user's ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Exercise_plan instances
        """
        return self.db.query(models.Exercise_plan).filter(
            models.Exercise_plan.user_owner_id == user_id
        ).offset(skip).limit(limit).all()

    def get_by_type(
        self,
        plan_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[models.Exercise_plan]:
        """
        Retrieve exercise plans by type with pagination.

        Args:
            plan_type: The exercise plan type
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Exercise_plan instances matching the type
        """
        return self.db.query(models.Exercise_plan).filter(
            models.Exercise_plan.exercise_plan_type == plan_type
        ).offset(skip).limit(limit).all()

    def get_by_difficulty(
        self,
        difficulty: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[models.Exercise_plan]:
        """
        Retrieve exercise plans by difficulty level with pagination.

        Args:
            difficulty: The difficulty level
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Exercise_plan instances matching the difficulty
        """
        return self.db.query(models.Exercise_plan).filter(
            models.Exercise_plan.difficult_level == difficulty
        ).offset(skip).limit(limit).all()

    def create_from_global(
        self,
        exercise_plan_global: models.Exercise_plan_global,
        user_id: int
    ) -> models.Exercise_plan:
        """
        Create a local exercise plan from a global template.

        This method copies all routines and exercises from the global
        exercise plan to create a user-specific instance.

        Args:
            exercise_plan_global: The global exercise plan template
            user_id: The user to assign the plan to

        Returns:
            The created Exercise_plan instance
        """
        # Create the exercise plan
        db_exercise_plan = models.Exercise_plan(
            exercise_plan_name=exercise_plan_global.exercise_plan_name,
            user_owner_id=user_id,
            exercise_plan_type=exercise_plan_global.exercise_plan_type,
            creation_date=datetime.now().date(),
            difficult_level=exercise_plan_global.difficult_level,
            routine_group_order=exercise_plan_global.routine_group_order
        )
        self.db.add(db_exercise_plan)
        self.db.flush()

        # Copy routines from global plan
        for rutine_global in exercise_plan_global.rutines:
            db_rutine = models.Rutine(
                rutine_name=rutine_global.rutine_name,
                rutine_type=rutine_global.rutine_type,
                rutine_group=rutine_global.rutine_group,
                rutine_category=rutine_global.rutine_category,
                exercise_plan_id=db_exercise_plan.exercise_plan_id,
                rounds=rutine_global.rounds,
                rst_btw_exercises=rutine_global.rst_btw_exercises,
                rst_btw_rounds=rutine_global.rst_btw_rounds,
                difficult_level=rutine_global.difficult_level
            )
            self.db.add(db_rutine)
            self.db.flush()

            # Copy exercises from global routine
            for exercise_global in rutine_global.exercises:
                db_exercise = models.Exercise(
                    exercise_name=exercise_global.exercise_name,
                    rep=exercise_global.rep,
                    exercise_type=exercise_global.exercise_type,
                    exercise_group=exercise_global.exercise_group,
                    rutine_id=db_rutine.rutine_id,
                    image=exercise_global.image
                )
                self.db.add(db_exercise)

        self.db.commit()
        return db_exercise_plan

    def assign_to_user(
        self,
        exercise_plan: schemas.Exercise_plan_Create,
        user_id: int
    ) -> models.Exercise_plan:
        """
        Assign an exercise plan to a user from schema data.

        Args:
            exercise_plan: The exercise plan creation schema
            user_id: The user to assign the plan to

        Returns:
            The created Exercise_plan instance
        """
        db_exercise_plan = models.Exercise_plan(
            exercise_plan_name=exercise_plan.exercise_plan_name,
            user_owner_id=user_id,
            exercise_plan_type=exercise_plan.exercise_plan_type,
            creation_date=datetime.now().date(),
            difficult_level=exercise_plan.difficult_level,
            routine_group_order=exercise_plan.routine_group_order
        )
        self.db.add(db_exercise_plan)
        self.db.flush()

        # Copy routines
        for rutine in exercise_plan.rutines:
            db_rutine = models.Rutine(
                rutine_name=rutine.rutine_name,
                rutine_type=rutine.rutine_type,
                rutine_group=rutine.rutine_group,
                rutine_category=rutine.rutine_category,
                exercise_plan_id=db_exercise_plan.exercise_plan_id,
                rounds=rutine.rounds,
                rst_btw_exercises=rutine.rst_btw_exercises,
                rst_btw_rounds=rutine.rst_btw_rounds,
                difficult_level=rutine.difficult_level
            )
            self.db.add(db_rutine)
            self.db.flush()

            # Copy exercises
            for exercise in rutine.exercises:
                db_exercise = models.Exercise(
                    exercise_name=exercise.exercise_name,
                    rep=exercise.rep,
                    exercise_type=exercise.exercise_type,
                    exercise_group=exercise.exercise_group,
                    rutine_id=db_rutine.rutine_id,
                    image=exercise.image
                )
                self.db.add(db_exercise)

        self.db.commit()
        return db_exercise_plan

    def delete_for_user(self, user_id: int) -> bool:
        """
        Delete exercise plan and all related data for a user.

        This cascades the deletion to routines and exercises using subqueries
        to avoid N+1 query performance issues.

        Args:
            user_id: The user's ID

        Returns:
            True if deleted, False if no plan found
        """
        exercise_plan = self.get_by_user_id(user_id)
        if not exercise_plan:
            return False

        # Subquery to get all routine IDs for this exercise plan
        routine_ids_subquery = self.db.query(models.Rutine.rutine_id).filter(
            models.Rutine.exercise_plan_id == exercise_plan.exercise_plan_id
        ).subquery()

        # Delete all exercises using subquery (single query instead of N queries)
        self.db.query(models.Exercise).filter(
            models.Exercise.rutine_id.in_(routine_ids_subquery)
        ).delete(synchronize_session=False)

        # Delete all routines for this exercise plan
        self.db.query(models.Rutine).filter(
            models.Rutine.exercise_plan_id == exercise_plan.exercise_plan_id
        ).delete(synchronize_session=False)

        # Delete the exercise plan
        self.db.query(models.Exercise_plan).filter(
            models.Exercise_plan.user_owner_id == user_id
        ).delete(synchronize_session=False)

        self.db.commit()
        return True

    def delete(self, exercise_plan_id: int) -> bool:
        """
        Delete an exercise plan by ID.

        Args:
            exercise_plan_id: The exercise plan's primary key

        Returns:
            True if deleted, False if not found
        """
        plan = self.get_by_id(exercise_plan_id)
        if plan:
            self.db.delete(plan)
            self.db.commit()
            return True
        return False

    def user_has_plan(self, user_id: int) -> bool:
        """
        Check if a user has an active exercise plan.

        Args:
            user_id: The user's ID

        Returns:
            True if user has a plan, False otherwise
        """
        return self.get_by_user_id(user_id) is not None

    def update_routine_order(
        self,
        exercise_plan_id: int,
        routine_order: list
    ) -> models.Exercise_plan | None:
        """
        Update the routine group order for an exercise plan.

        Args:
            exercise_plan_id: The exercise plan's primary key
            routine_order: The new routine order list

        Returns:
            The updated Exercise_plan instance if found, None otherwise
        """
        plan = self.get_by_id(exercise_plan_id)
        if plan:
            plan.routine_group_order = routine_order
            self.db.add(plan)
            self.db.commit()
            self.db.refresh(plan)
            return plan
        return None
