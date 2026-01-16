"""
Routine Global Repository implementation.

This module provides data access operations for Rutine_global entities,
encapsulating all global routine-related database queries.
"""

from typing import Sequence

from sqlalchemy.orm import Session, joinedload

import models
import schemas
from infrastructure.database.repositories.base_repository import BaseRepository


class RoutineGlobalRepository(BaseRepository[models.Rutine_global, schemas.Rutine_global_Create, schemas.Rutine_global_Base]):
    """
    Repository for Rutine_global entity operations.

    Provides methods for global routine template CRUD operations
    and specific domain queries.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize the Routine Global repository.

        Args:
            db: The database session
        """
        super().__init__(models.Rutine_global, db)

    def get_by_id(self, rutine_id: int) -> models.Rutine_global | None:
        """
        Retrieve a global routine by its ID.

        Args:
            rutine_id: The routine's primary key

        Returns:
            The Rutine_global instance if found, None otherwise
        """
        return self.db.query(models.Rutine_global).filter(
            models.Rutine_global.rutine_id == rutine_id
        ).first()

    def get_by_id_with_exercises(self, rutine_id: int) -> models.Rutine_global | None:
        """
        Retrieve a global routine with exercises eagerly loaded.

        Args:
            rutine_id: The routine's primary key

        Returns:
            The Rutine_global instance with exercises if found, None otherwise
        """
        return self.db.query(models.Rutine_global)\
            .options(joinedload(models.Rutine_global.exercises))\
            .filter(models.Rutine_global.rutine_id == rutine_id)\
            .first()

    def get_by_exercise_plan_id(self, exercise_plan_id: int) -> Sequence[models.Rutine_global]:
        """
        Retrieve all global routines for a specific exercise plan.

        Args:
            exercise_plan_id: The exercise plan's ID

        Returns:
            List of Rutine_global instances
        """
        return self.db.query(models.Rutine_global).filter(
            models.Rutine_global.exercise_plan_id == exercise_plan_id
        ).all()

    def get_by_name_and_plan(
        self,
        rutine_name: str,
        exercise_plan_id: int
    ) -> models.Rutine_global | None:
        """
        Retrieve a global routine by name within a specific plan.

        Args:
            rutine_name: The routine name
            exercise_plan_id: The exercise plan's ID

        Returns:
            The Rutine_global instance if found, None otherwise
        """
        return self.db.query(models.Rutine_global).filter(
            models.Rutine_global.rutine_name == rutine_name,
            models.Rutine_global.exercise_plan_id == exercise_plan_id
        ).first()

    def get_by_type(self, rutine_type: str) -> Sequence[models.Rutine_global]:
        """
        Retrieve global routines by type.

        Args:
            rutine_type: The routine type

        Returns:
            List of Rutine_global instances matching the type
        """
        return self.db.query(models.Rutine_global).filter(
            models.Rutine_global.rutine_type == rutine_type
        ).all()

    def get_by_group(self, rutine_group: str) -> Sequence[models.Rutine_global]:
        """
        Retrieve global routines by group.

        Args:
            rutine_group: The routine group

        Returns:
            List of Rutine_global instances matching the group
        """
        return self.db.query(models.Rutine_global).filter(
            models.Rutine_global.rutine_group == rutine_group
        ).all()

    def get_by_category(self, rutine_category: str) -> Sequence[models.Rutine_global]:
        """
        Retrieve global routines by category.

        Args:
            rutine_category: The routine category

        Returns:
            List of Rutine_global instances matching the category
        """
        return self.db.query(models.Rutine_global).filter(
            models.Rutine_global.rutine_category == rutine_category
        ).all()

    def get_by_difficulty(self, difficulty: str) -> Sequence[models.Rutine_global]:
        """
        Retrieve global routines by difficulty level.

        Args:
            difficulty: The difficulty level

        Returns:
            List of Rutine_global instances matching the difficulty
        """
        return self.db.query(models.Rutine_global).filter(
            models.Rutine_global.difficult_level == difficulty
        ).all()

    def create(self, routine: schemas.Rutine_global_Create) -> models.Rutine_global:
        """
        Create a new global routine.

        Args:
            routine: The routine creation schema

        Returns:
            The created Rutine_global instance
        """
        db_rutine = models.Rutine_global(
            rutine_name=routine.rutine_name,
            rutine_type=routine.rutine_type,
            rutine_group=routine.rutine_group,
            rutine_category=routine.rutine_category,
            exercise_plan_id=routine.exercise_plan_id,
            rounds=routine.rounds,
            rst_btw_exercises=routine.rst_btw_exercises,
            rst_btw_rounds=routine.rst_btw_rounds,
            difficult_level=routine.difficult_level
        )
        self.db.add(db_rutine)
        self.db.commit()
        self.db.refresh(db_rutine)
        return db_rutine

    def create_from_dict(self, routine_data: dict, exercise_plan_id: int) -> models.Rutine_global:
        """
        Create a new global routine from dictionary data.

        Args:
            routine_data: Dictionary with routine data
            exercise_plan_id: The parent exercise plan ID

        Returns:
            The created Rutine_global instance
        """
        db_rutine = models.Rutine_global(
            rutine_name=routine_data.get('rutine_name'),
            rutine_type=routine_data.get('rutine_type'),
            rutine_group=routine_data.get('rutine_group'),
            rutine_category=routine_data.get('rutine_category'),
            exercise_plan_id=exercise_plan_id,
            rounds=routine_data.get('rounds', 0),
            rst_btw_exercises=routine_data.get('rst_btw_exercises', '0'),
            rst_btw_rounds=routine_data.get('rst_btw_rounds', '0'),
            difficult_level=routine_data.get('difficult_level')
        )
        self.db.add(db_rutine)
        self.db.commit()
        self.db.refresh(db_rutine)
        return db_rutine

    def exists_in_plan(self, exercise_plan_id: int, rutine_name: str) -> bool:
        """
        Check if a routine with the given name exists in the plan.

        Args:
            exercise_plan_id: The exercise plan's ID
            rutine_name: The routine name to check

        Returns:
            True if routine exists, False otherwise
        """
        return self.get_by_name_and_plan(rutine_name, exercise_plan_id) is not None

    def delete(self, rutine_id: int) -> bool:
        """
        Delete a global routine by ID.

        This cascades to associated exercises.

        Args:
            rutine_id: The routine's primary key

        Returns:
            True if deleted, False if not found
        """
        routine = self.get_by_id(rutine_id)
        if routine:
            self.db.delete(routine)
            self.db.commit()
            return True
        return False

    def delete_by_exercise_plan(self, exercise_plan_id: int) -> int:
        """
        Delete all global routines for an exercise plan.

        Args:
            exercise_plan_id: The exercise plan's ID

        Returns:
            Number of routines deleted
        """
        result = self.db.query(models.Rutine_global).filter(
            models.Rutine_global.exercise_plan_id == exercise_plan_id
        ).delete()
        self.db.commit()
        return result

    def update(
        self,
        rutine_id: int,
        update_data: dict
    ) -> models.Rutine_global | None:
        """
        Update a global routine.

        Args:
            rutine_id: The routine's primary key
            update_data: Dictionary with fields to update

        Returns:
            The updated Rutine_global instance if found, None otherwise
        """
        routine = self.get_by_id(rutine_id)
        if routine:
            for field, value in update_data.items():
                if hasattr(routine, field) and value is not None:
                    setattr(routine, field, value)
            self.db.add(routine)
            self.db.commit()
            self.db.refresh(routine)
            return routine
        return None

    def count_by_exercise_plan(self, exercise_plan_id: int) -> int:
        """
        Count global routines in an exercise plan.

        Args:
            exercise_plan_id: The exercise plan's ID

        Returns:
            Number of routines in the plan
        """
        return self.db.query(models.Rutine_global).filter(
            models.Rutine_global.exercise_plan_id == exercise_plan_id
        ).count()

    def get_routine_groups_for_plan(self, exercise_plan_id: int) -> list[str]:
        """
        Get all unique routine groups for an exercise plan.

        Args:
            exercise_plan_id: The exercise plan's ID

        Returns:
            List of unique routine group names
        """
        routines = self.get_by_exercise_plan_id(exercise_plan_id)
        return list(set(routine.rutine_group for routine in routines if routine.rutine_group))
