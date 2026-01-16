"""
Exercise Plan Global Repository implementation.

This module provides data access operations for Exercise_plan_global entities,
encapsulating all global exercise plan-related database queries.
"""

from typing import Sequence
from datetime import datetime

from sqlalchemy.orm import Session, joinedload

import models
import schemas
from infrastructure.database.repositories.base_repository import BaseRepository


class ExercisePlanGlobalRepository(BaseRepository[models.Exercise_plan_global, schemas.Exercise_plan_global_Create, schemas.Exercise_plan_global_Base]):
    """
    Repository for Exercise_plan_global entity operations.

    Provides methods for global exercise plan template CRUD operations
    and specific domain queries.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize the Exercise Plan Global repository.

        Args:
            db: The database session
        """
        super().__init__(models.Exercise_plan_global, db)

    def get_by_id(self, exercise_plan_id: int) -> models.Exercise_plan_global | None:
        """
        Retrieve a global exercise plan by its ID.

        Args:
            exercise_plan_id: The exercise plan's primary key

        Returns:
            The Exercise_plan_global instance if found, None otherwise
        """
        return self.db.query(models.Exercise_plan_global).filter(
            models.Exercise_plan_global.exercise_plan_id == exercise_plan_id
        ).first()

    def get_by_id_with_routines(self, exercise_plan_id: int) -> models.Exercise_plan_global | None:
        """
        Retrieve a global exercise plan with routines eagerly loaded.

        Args:
            exercise_plan_id: The exercise plan's primary key

        Returns:
            The Exercise_plan_global instance with routines if found, None otherwise
        """
        return self.db.query(models.Exercise_plan_global)\
            .options(joinedload(models.Exercise_plan_global.rutines))\
            .filter(models.Exercise_plan_global.exercise_plan_id == exercise_plan_id)\
            .first()

    def get_by_name(self, exercise_plan_name: str) -> models.Exercise_plan_global | None:
        """
        Retrieve a global exercise plan by name.

        Args:
            exercise_plan_name: The exercise plan name

        Returns:
            The Exercise_plan_global instance if found, None otherwise
        """
        return self.db.query(models.Exercise_plan_global).filter(
            models.Exercise_plan_global.exercise_plan_name == exercise_plan_name
        ).first()

    def get_by_type(self, plan_type: str) -> Sequence[models.Exercise_plan_global]:
        """
        Retrieve all global exercise plans by type.

        Args:
            plan_type: The exercise plan type

        Returns:
            List of Exercise_plan_global instances matching the type
        """
        return self.db.query(models.Exercise_plan_global).filter(
            models.Exercise_plan_global.exercise_plan_type == plan_type
        ).all()

    def get_by_difficulty(self, difficulty: str) -> Sequence[models.Exercise_plan_global]:
        """
        Retrieve global exercise plans by difficulty level.

        Args:
            difficulty: The difficulty level

        Returns:
            List of Exercise_plan_global instances matching the difficulty
        """
        return self.db.query(models.Exercise_plan_global).filter(
            models.Exercise_plan_global.difficult_level == difficulty
        ).all()

    def get_by_creator(self, user_id: int) -> Sequence[models.Exercise_plan_global]:
        """
        Retrieve all global exercise plans created by a user.

        Args:
            user_id: The creator's user ID

        Returns:
            List of Exercise_plan_global instances
        """
        return self.db.query(models.Exercise_plan_global).filter(
            models.Exercise_plan_global.user_creator_id == user_id
        ).all()

    def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[models.Exercise_plan_global]:
        """
        Retrieve all global exercise plans with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Exercise_plan_global instances
        """
        return self.db.query(models.Exercise_plan_global).offset(skip).limit(limit).all()

    def create(
        self,
        exercise_plan: schemas.Exercise_plan_global_Create,
        user_id: int
    ) -> models.Exercise_plan_global:
        """
        Create a new global exercise plan.

        Args:
            exercise_plan: The exercise plan creation schema
            user_id: The creator's user ID

        Returns:
            The created Exercise_plan_global instance
        """
        db_exercise_plan = models.Exercise_plan_global(
            exercise_plan_name=exercise_plan.exercise_plan_name,
            exercise_plan_type=exercise_plan.exercise_plan_type,
            difficult_level=exercise_plan.difficult_level,
            user_creator_id=user_id,
            creation_date=datetime.now().date()
        )
        self.db.add(db_exercise_plan)
        self.db.commit()
        self.db.refresh(db_exercise_plan)
        return db_exercise_plan

    def create_full(
        self,
        exercise_plan_data: dict,
        user_id: int
    ) -> models.Exercise_plan_global:
        """
        Create a complete global exercise plan with routines and exercises.

        Args:
            exercise_plan_data: Dictionary with full exercise plan data
            user_id: The creator's user ID

        Returns:
            The created Exercise_plan_global instance
        """
        # Create the exercise plan
        db_exercise_plan = models.Exercise_plan_global(
            exercise_plan_name=exercise_plan_data.get('exercise_plan_name'),
            exercise_plan_type=exercise_plan_data.get('exercise_plan_type'),
            difficult_level=exercise_plan_data.get('difficult_level'),
            user_creator_id=user_id,
            creation_date=datetime.now().date()
        )
        self.db.add(db_exercise_plan)
        self.db.flush()

        # Create routines
        for rutine_data in exercise_plan_data.get('rutines', []):
            db_rutine = models.Rutine_global(
                rutine_name=rutine_data.get('rutine_name'),
                rutine_type=db_exercise_plan.exercise_plan_type,
                rutine_group=rutine_data.get('rutine_group'),
                rutine_category=rutine_data.get('rutine_category'),
                exercise_plan_id=db_exercise_plan.exercise_plan_id,
                rounds=rutine_data.get('rounds', 0),
                rst_btw_exercises=rutine_data.get('rst_btw_exercises', '0'),
                rst_btw_rounds=rutine_data.get('rst_btw_rounds', '0'),
                difficult_level=rutine_data.get('difficult_level')
            )
            self.db.add(db_rutine)
            self.db.flush()

            # Create exercises
            for exercise_data in rutine_data.get('exercises', []):
                db_exercise = models.Exercise_global(
                    exercise_name=exercise_data.get('exercise_name'),
                    rep=exercise_data.get('rep'),
                    exercise_type=exercise_data.get('exercise_type'),
                    exercise_group=db_rutine.rutine_group,
                    rutine_id=db_rutine.rutine_id,
                    image=exercise_data.get('image', 'empty')
                )
                self.db.add(db_exercise)

        self.db.commit()
        self.db.refresh(db_exercise_plan)
        return db_exercise_plan

    def name_exists(self, exercise_plan_name: str) -> bool:
        """
        Check if an exercise plan name already exists.

        Args:
            exercise_plan_name: The name to check

        Returns:
            True if name exists, False otherwise
        """
        return self.get_by_name(exercise_plan_name) is not None

    def delete(self, exercise_plan_id: int) -> bool:
        """
        Delete a global exercise plan by ID.

        This cascades to routines and exercises.

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

    def update(
        self,
        exercise_plan_id: int,
        update_data: dict
    ) -> models.Exercise_plan_global | None:
        """
        Update a global exercise plan.

        Args:
            exercise_plan_id: The exercise plan's primary key
            update_data: Dictionary with fields to update

        Returns:
            The updated Exercise_plan_global instance if found, None otherwise
        """
        plan = self.get_by_id(exercise_plan_id)
        if plan:
            for field, value in update_data.items():
                if hasattr(plan, field) and value is not None:
                    setattr(plan, field, value)
            self.db.add(plan)
            self.db.commit()
            self.db.refresh(plan)
            return plan
        return None

    def search_by_type_and_difficulty(
        self,
        plan_type: str | None = None,
        difficulty: str | None = None
    ) -> Sequence[models.Exercise_plan_global]:
        """
        Search global exercise plans by type and/or difficulty.

        Args:
            plan_type: Optional filter by type
            difficulty: Optional filter by difficulty

        Returns:
            List of matching Exercise_plan_global instances
        """
        query = self.db.query(models.Exercise_plan_global)

        if plan_type:
            query = query.filter(
                models.Exercise_plan_global.exercise_plan_type == plan_type
            )

        if difficulty:
            query = query.filter(
                models.Exercise_plan_global.difficult_level == difficulty
            )

        return query.all()

    def count_by_type(self, plan_type: str) -> int:
        """
        Count global exercise plans of a specific type.

        Args:
            plan_type: The exercise plan type

        Returns:
            Number of plans of that type
        """
        return self.db.query(models.Exercise_plan_global).filter(
            models.Exercise_plan_global.exercise_plan_type == plan_type
        ).count()
