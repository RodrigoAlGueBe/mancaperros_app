"""
Routine Repository implementation.

This module provides data access operations for Rutine entities,
encapsulating all routine-related database queries.
"""

from typing import Sequence

from sqlalchemy.orm import Session, joinedload

import models
import schemas
from infrastructure.database.repositories.base_repository import BaseRepository


class RoutineRepository(BaseRepository[models.Rutine, schemas.Rutine_Create, schemas.Rutine_Base]):
    """
    Repository for Rutine entity operations.

    Provides methods for routine CRUD operations and
    specific domain queries.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize the Routine repository.

        Args:
            db: The database session
        """
        super().__init__(models.Rutine, db)

    def get_by_id(self, rutine_id: int) -> models.Rutine | None:
        """
        Retrieve a routine by its ID.

        Args:
            rutine_id: The routine's primary key

        Returns:
            The Rutine instance if found, None otherwise
        """
        return self.db.query(models.Rutine).filter(
            models.Rutine.rutine_id == rutine_id
        ).first()

    def get_by_id_with_exercises(self, rutine_id: int) -> models.Rutine | None:
        """
        Retrieve a routine with its exercises eagerly loaded.

        Args:
            rutine_id: The routine's primary key

        Returns:
            The Rutine instance with exercises if found, None otherwise
        """
        return self.db.query(models.Rutine)\
            .options(joinedload(models.Rutine.exercises))\
            .filter(models.Rutine.rutine_id == rutine_id)\
            .first()

    def get_by_exercise_plan_id(
        self,
        exercise_plan_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[models.Rutine]:
        """
        Retrieve all routines for a specific exercise plan with pagination.

        Args:
            exercise_plan_id: The exercise plan's ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Rutine instances
        """
        return self.db.query(models.Rutine).filter(
            models.Rutine.exercise_plan_id == exercise_plan_id
        ).offset(skip).limit(limit).all()

    def get_by_exercise_plan_and_group(
        self,
        exercise_plan_id: int,
        routine_group: str
    ) -> models.Rutine | None:
        """
        Retrieve a routine by exercise plan and group.

        Args:
            exercise_plan_id: The exercise plan's ID
            routine_group: The routine group name

        Returns:
            The Rutine instance if found, None otherwise
        """
        return self.db.query(models.Rutine).filter(
            models.Rutine.exercise_plan_id == exercise_plan_id,
            models.Rutine.rutine_group == routine_group
        ).first()

    def get_by_type(
        self,
        rutine_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[models.Rutine]:
        """
        Retrieve routines by type with pagination.

        Args:
            rutine_type: The routine type
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Rutine instances matching the type
        """
        return self.db.query(models.Rutine).filter(
            models.Rutine.rutine_type == rutine_type
        ).offset(skip).limit(limit).all()

    def get_by_group(
        self,
        rutine_group: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[models.Rutine]:
        """
        Retrieve routines by group with pagination.

        Args:
            rutine_group: The routine group
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Rutine instances matching the group
        """
        return self.db.query(models.Rutine).filter(
            models.Rutine.rutine_group == rutine_group
        ).offset(skip).limit(limit).all()

    def get_by_category(
        self,
        rutine_category: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[models.Rutine]:
        """
        Retrieve routines by category with pagination.

        Args:
            rutine_category: The routine category
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Rutine instances matching the category
        """
        return self.db.query(models.Rutine).filter(
            models.Rutine.rutine_category == rutine_category
        ).offset(skip).limit(limit).all()

    def get_by_difficulty(
        self,
        difficulty: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[models.Rutine]:
        """
        Retrieve routines by difficulty level with pagination.

        Args:
            difficulty: The difficulty level
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Rutine instances matching the difficulty
        """
        return self.db.query(models.Rutine).filter(
            models.Rutine.difficult_level == difficulty
        ).offset(skip).limit(limit).all()

    def create(self, routine: schemas.Rutine_Create, exercise_plan_id: int) -> models.Rutine:
        """
        Create a new routine.

        Args:
            routine: The routine creation schema
            exercise_plan_id: The parent exercise plan ID

        Returns:
            The created Rutine instance
        """
        db_rutine = models.Rutine(
            rutine_name=routine.rutine_name,
            rutine_type=routine.rutine_type,
            rutine_group=routine.rutine_group,
            rutine_category=routine.rutine_category,
            exercise_plan_id=exercise_plan_id,
            rounds=getattr(routine, 'rounds', 0),
            rst_btw_exercises=getattr(routine, 'rst_btw_exercises', '0'),
            rst_btw_rounds=getattr(routine, 'rst_btw_rounds', '0'),
            difficult_level=getattr(routine, 'difficult_level', None)
        )
        self.db.add(db_rutine)
        self.db.commit()
        self.db.refresh(db_rutine)
        return db_rutine

    def update(self, routine: models.Rutine) -> models.Rutine:
        """
        Update an existing routine.

        Args:
            routine: The routine instance with updated values

        Returns:
            The updated Rutine instance
        """
        self.db.add(routine)
        self.db.commit()
        self.db.refresh(routine)
        return routine

    def delete(self, rutine_id: int) -> bool:
        """
        Delete a routine by ID.

        This will cascade delete associated exercises.

        Args:
            rutine_id: The routine's primary key

        Returns:
            True if deleted, False if not found
        """
        routine = self.get_by_id(rutine_id)
        if routine:
            # Delete associated exercises first
            self.db.query(models.Exercise).filter(
                models.Exercise.rutine_id == rutine_id
            ).delete()
            self.db.delete(routine)
            self.db.commit()
            return True
        return False

    def delete_by_exercise_plan(self, exercise_plan_id: int) -> int:
        """
        Delete all routines for an exercise plan.

        Uses subquery to delete exercises in a single query, avoiding N+1
        query performance issues.

        Args:
            exercise_plan_id: The exercise plan's ID

        Returns:
            Number of routines deleted
        """
        # Count routines before deletion
        count = self.db.query(models.Rutine).filter(
            models.Rutine.exercise_plan_id == exercise_plan_id
        ).count()

        # Subquery to get all routine IDs for this exercise plan
        routine_ids_subquery = self.db.query(models.Rutine.rutine_id).filter(
            models.Rutine.exercise_plan_id == exercise_plan_id
        ).subquery()

        # Delete all exercises using subquery (single query instead of N queries)
        self.db.query(models.Exercise).filter(
            models.Exercise.rutine_id.in_(routine_ids_subquery)
        ).delete(synchronize_session=False)

        # Delete all routines for this exercise plan
        self.db.query(models.Rutine).filter(
            models.Rutine.exercise_plan_id == exercise_plan_id
        ).delete(synchronize_session=False)

        self.db.commit()
        return count

    def get_routine_groups_for_plan(self, exercise_plan_id: int) -> list[dict]:
        """
        Get all routine groups with their IDs for an exercise plan.

        Args:
            exercise_plan_id: The exercise plan's ID

        Returns:
            List of dicts with rutine_group and rutine_id
        """
        routines = self.get_by_exercise_plan_id(exercise_plan_id)
        return [
            {"rutine_group": routine.rutine_group, "rutine_id": routine.rutine_id}
            for routine in routines
        ]

    def exists_in_plan(self, exercise_plan_id: int, rutine_name: str) -> bool:
        """
        Check if a routine with the given name exists in the plan.

        Args:
            exercise_plan_id: The exercise plan's ID
            rutine_name: The routine name to check

        Returns:
            True if routine exists, False otherwise
        """
        return self.db.query(models.Rutine).filter(
            models.Rutine.exercise_plan_id == exercise_plan_id,
            models.Rutine.rutine_name == rutine_name
        ).first() is not None

    def update_rounds(self, rutine_id: int, rounds: int) -> models.Rutine | None:
        """
        Update the number of rounds for a routine.

        Args:
            rutine_id: The routine's primary key
            rounds: The new number of rounds

        Returns:
            The updated Rutine instance if found, None otherwise
        """
        routine = self.get_by_id(rutine_id)
        if routine:
            routine.rounds = rounds
            self.db.add(routine)
            self.db.commit()
            self.db.refresh(routine)
            return routine
        return None

    def update_rest_times(
        self,
        rutine_id: int,
        rst_btw_exercises: str | None = None,
        rst_btw_rounds: str | None = None
    ) -> models.Rutine | None:
        """
        Update rest times for a routine.

        Args:
            rutine_id: The routine's primary key
            rst_btw_exercises: Rest time between exercises (optional)
            rst_btw_rounds: Rest time between rounds (optional)

        Returns:
            The updated Rutine instance if found, None otherwise
        """
        routine = self.get_by_id(rutine_id)
        if routine:
            if rst_btw_exercises is not None:
                routine.rst_btw_exercises = rst_btw_exercises
            if rst_btw_rounds is not None:
                routine.rst_btw_rounds = rst_btw_rounds
            self.db.add(routine)
            self.db.commit()
            self.db.refresh(routine)
            return routine
        return None
