"""
Exercise Plan Repository - Repository for Exercise Plan entities.

This module encapsulates all database operations related to Exercise Plan
and Exercise Plan Global entities.
"""

from typing import Optional, List, Any, Dict
from datetime import datetime, date

from sqlalchemy.orm import Session, joinedload

from .base_repository import BaseRepository

# Import models
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
import models


class ExercisePlanRepository(BaseRepository[models.Exercise_plan, Any, Any]):
    """
    Repository for Exercise_plan (user-assigned) entity operations.

    Handles operations for exercise plans that are assigned to specific users,
    including creation, retrieval, and cascading deletions.
    """

    def __init__(self, db: Session):
        """
        Initialize the ExercisePlanRepository.

        Args:
            db: The database session
        """
        super().__init__(models.Exercise_plan, db)

    def get_by_id(self, exercise_plan_id: int) -> Optional[models.Exercise_plan]:
        """
        Retrieve an exercise plan by its ID.

        Args:
            exercise_plan_id: The exercise plan's primary key

        Returns:
            The Exercise_plan if found, None otherwise
        """
        return self.db.query(models.Exercise_plan).filter(
            models.Exercise_plan.exercise_plan_id == exercise_plan_id
        ).first()

    def get_by_id_with_routines(self, exercise_plan_id: int) -> Optional[models.Exercise_plan]:
        """
        Retrieve an exercise plan with its routines eagerly loaded.

        Args:
            exercise_plan_id: The exercise plan's primary key

        Returns:
            The Exercise_plan with loaded routines if found, None otherwise
        """
        return self.db.query(models.Exercise_plan).options(
            joinedload(models.Exercise_plan.rutines)
        ).filter(
            models.Exercise_plan.exercise_plan_id == exercise_plan_id
        ).first()

    def get_by_user_id(self, user_id: int) -> Optional[models.Exercise_plan]:
        """
        Retrieve an exercise plan for a specific user.

        Args:
            user_id: The user's ID

        Returns:
            The Exercise_plan if found, None otherwise
        """
        return self.db.query(models.Exercise_plan).filter(
            models.Exercise_plan.user_owner_id == user_id
        ).first()

    def get_all_by_user_id(self, user_id: int) -> List[models.Exercise_plan]:
        """
        Retrieve all exercise plans for a specific user.

        Args:
            user_id: The user's ID

        Returns:
            List of Exercise_plan entities
        """
        return self.db.query(models.Exercise_plan).filter(
            models.Exercise_plan.user_owner_id == user_id
        ).all()

    def create(
        self,
        exercise_plan_name: str,
        user_owner_id: int,
        exercise_plan_type: str,
        difficult_level: str,
        routine_group_order: List[str]
    ) -> models.Exercise_plan:
        """
        Create a new exercise plan for a user.

        Args:
            exercise_plan_name: Name of the exercise plan
            user_owner_id: The owner user's ID
            exercise_plan_type: Type of the exercise plan
            difficult_level: Difficulty level
            routine_group_order: Order of routine groups

        Returns:
            The created Exercise_plan entity
        """
        db_exercise_plan = models.Exercise_plan(
            exercise_plan_name=exercise_plan_name,
            user_owner_id=user_owner_id,
            exercise_plan_type=exercise_plan_type,
            creation_date=datetime.now().date(),
            difficult_level=difficult_level,
            routine_group_order=routine_group_order
        )
        self.db.add(db_exercise_plan)
        self.db.commit()
        self.db.refresh(db_exercise_plan)
        return db_exercise_plan

    def create_without_commit(
        self,
        exercise_plan_name: str,
        user_owner_id: int,
        exercise_plan_type: str,
        difficult_level: str,
        routine_group_order: List[str]
    ) -> models.Exercise_plan:
        """
        Create a new exercise plan without committing (for transaction batching).

        Args:
            exercise_plan_name: Name of the exercise plan
            user_owner_id: The owner user's ID
            exercise_plan_type: Type of the exercise plan
            difficult_level: Difficulty level
            routine_group_order: Order of routine groups

        Returns:
            The created Exercise_plan entity (not committed)
        """
        db_exercise_plan = models.Exercise_plan(
            exercise_plan_name=exercise_plan_name,
            user_owner_id=user_owner_id,
            exercise_plan_type=exercise_plan_type,
            creation_date=datetime.now().date(),
            difficult_level=difficult_level,
            routine_group_order=routine_group_order
        )
        self.db.add(db_exercise_plan)
        self.db.flush()
        return db_exercise_plan

    def assign_from_global(
        self,
        exercise_plan_global: models.Exercise_plan_global,
        user_id: int
    ) -> models.Exercise_plan:
        """
        Assign a global exercise plan to a user by copying it.

        This creates a complete copy of the global exercise plan including
        all routines and exercises.

        Args:
            exercise_plan_global: The global exercise plan to copy
            user_id: The user to assign the plan to

        Returns:
            The created Exercise_plan entity
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

        # Copy routines
        for routine_global in exercise_plan_global.rutines:
            db_routine = models.Rutine(
                rutine_name=routine_global.rutine_name,
                rutine_type=routine_global.rutine_type,
                rutine_group=routine_global.rutine_group,
                rutine_category=routine_global.rutine_category,
                exercise_plan_id=db_exercise_plan.exercise_plan_id,
                rounds=routine_global.rounds,
                rst_btw_exercises=routine_global.rst_btw_exercises,
                rst_btw_rounds=routine_global.rst_btw_rounds,
                difficult_level=routine_global.difficult_level
            )
            self.db.add(db_routine)
            self.db.flush()

            # Copy exercises
            for exercise_global in routine_global.exercises:
                db_exercise = models.Exercise(
                    exercise_name=exercise_global.exercise_name,
                    rep=exercise_global.rep,
                    exercise_type=exercise_global.exercise_type,
                    exercise_group=exercise_global.exercise_group,
                    rutine_id=db_routine.rutine_id,
                    image=exercise_global.image
                )
                self.db.add(db_exercise)

        self.db.commit()
        return db_exercise_plan

    def delete_for_user(self, user_id: int) -> bool:
        """
        Delete all exercise plans and related data for a user.

        Performs cascading delete of exercise plan, routines, and exercises.

        Args:
            user_id: The user's ID

        Returns:
            True if deletion was successful
        """
        exercise_plan = self.get_by_user_id(user_id)
        if not exercise_plan:
            return False

        # Get all routines for the exercise plan
        routines = self.db.query(models.Rutine).filter(
            models.Rutine.exercise_plan_id == exercise_plan.exercise_plan_id
        ).all()

        # Delete exercises for each routine
        for routine in routines:
            self.db.query(models.Exercise).filter(
                models.Exercise.rutine_id == routine.rutine_id
            ).delete()

        # Delete routines
        self.db.query(models.Rutine).filter(
            models.Rutine.exercise_plan_id == exercise_plan.exercise_plan_id
        ).delete()

        # Delete exercise plan
        self.db.query(models.Exercise_plan).filter(
            models.Exercise_plan.user_owner_id == user_id
        ).delete()

        self.db.commit()
        return True

    def exists_for_user(self, user_id: int) -> bool:
        """
        Check if a user has an assigned exercise plan.

        Args:
            user_id: The user's ID

        Returns:
            True if the user has an exercise plan
        """
        return self.db.query(models.Exercise_plan).filter(
            models.Exercise_plan.user_owner_id == user_id
        ).first() is not None


class ExercisePlanGlobalRepository(BaseRepository[models.Exercise_plan_global, Any, Any]):
    """
    Repository for Exercise_plan_global (template) entity operations.

    Handles operations for global exercise plan templates that can be
    assigned to multiple users.
    """

    def __init__(self, db: Session):
        """
        Initialize the ExercisePlanGlobalRepository.

        Args:
            db: The database session
        """
        super().__init__(models.Exercise_plan_global, db)

    def get_by_id(self, exercise_plan_id: int) -> Optional[models.Exercise_plan_global]:
        """
        Retrieve a global exercise plan by its ID.

        Args:
            exercise_plan_id: The exercise plan's primary key

        Returns:
            The Exercise_plan_global if found, None otherwise
        """
        return self.db.query(models.Exercise_plan_global).filter(
            models.Exercise_plan_global.exercise_plan_id == exercise_plan_id
        ).first()

    def get_by_id_with_routines(
        self,
        exercise_plan_id: int
    ) -> Optional[models.Exercise_plan_global]:
        """
        Retrieve a global exercise plan with routines eagerly loaded.

        Args:
            exercise_plan_id: The exercise plan's primary key

        Returns:
            The Exercise_plan_global with loaded routines if found, None otherwise
        """
        return self.db.query(models.Exercise_plan_global).options(
            joinedload(models.Exercise_plan_global.rutines)
        ).filter(
            models.Exercise_plan_global.exercise_plan_id == exercise_plan_id
        ).first()

    def get_by_name(self, name: str) -> Optional[models.Exercise_plan_global]:
        """
        Retrieve a global exercise plan by its name.

        Args:
            name: The exercise plan name

        Returns:
            The Exercise_plan_global if found, None otherwise
        """
        return self.db.query(models.Exercise_plan_global).filter(
            models.Exercise_plan_global.exercise_plan_name == name
        ).first()

    def get_by_type(self, exercise_plan_type: str) -> List[models.Exercise_plan_global]:
        """
        Retrieve all global exercise plans of a specific type.

        Args:
            exercise_plan_type: The type to filter by

        Returns:
            List of Exercise_plan_global entities
        """
        return self.db.query(models.Exercise_plan_global).filter(
            models.Exercise_plan_global.exercise_plan_type == exercise_plan_type
        ).all()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.Exercise_plan_global]:
        """
        Retrieve all global exercise plans with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Exercise_plan_global entities
        """
        return self.db.query(models.Exercise_plan_global).offset(skip).limit(limit).all()

    def create(
        self,
        exercise_plan_name: str,
        user_creator_id: int,
        exercise_plan_type: str,
        difficult_level: str,
        routine_group_order: Optional[List[str]] = None
    ) -> models.Exercise_plan_global:
        """
        Create a new global exercise plan.

        Args:
            exercise_plan_name: Name of the exercise plan
            user_creator_id: The creator user's ID
            exercise_plan_type: Type of the exercise plan
            difficult_level: Difficulty level
            routine_group_order: Order of routine groups (optional)

        Returns:
            The created Exercise_plan_global entity
        """
        db_exercise_plan = models.Exercise_plan_global(
            exercise_plan_name=exercise_plan_name,
            user_creator_id=user_creator_id,
            exercise_plan_type=exercise_plan_type,
            creation_date=datetime.now().date(),
            difficult_level=difficult_level,
            routine_group_order=routine_group_order or []
        )
        self.db.add(db_exercise_plan)
        self.db.commit()
        self.db.refresh(db_exercise_plan)
        return db_exercise_plan

    def create_from_schema(
        self,
        exercise_plan_schema: Any,
        user_id: int
    ) -> models.Exercise_plan_global:
        """
        Create a new global exercise plan from a Pydantic schema.

        Args:
            exercise_plan_schema: The exercise plan creation schema
            user_id: The creator user's ID

        Returns:
            The created Exercise_plan_global entity
        """
        db_exercise_plan = models.Exercise_plan_global(
            **exercise_plan_schema.dict(),
            user_creator_id=user_id,
            creation_date=datetime.now().date()
        )
        self.db.add(db_exercise_plan)
        self.db.commit()
        self.db.refresh(db_exercise_plan)
        return db_exercise_plan

    def exists_by_name(self, name: str) -> bool:
        """
        Check if a global exercise plan exists with the given name.

        Args:
            name: The exercise plan name to check

        Returns:
            True if an exercise plan exists with that name
        """
        return self.db.query(models.Exercise_plan_global).filter(
            models.Exercise_plan_global.exercise_plan_name == name
        ).first() is not None

    def delete_by_id(self, exercise_plan_id: int) -> bool:
        """
        Delete a global exercise plan by its ID.

        Note: This will cascade delete related routines and exercises.

        Args:
            exercise_plan_id: The exercise plan's primary key

        Returns:
            True if deletion was successful, False if not found
        """
        deleted_count = self.db.query(models.Exercise_plan_global).filter(
            models.Exercise_plan_global.exercise_plan_id == exercise_plan_id
        ).delete()
        self.db.commit()
        return deleted_count > 0
