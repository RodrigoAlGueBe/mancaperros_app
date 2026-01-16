"""
Exercise Global Repository implementation.

This module provides data access operations for Exercise_global entities,
encapsulating all global exercise-related database queries.
"""

from typing import Sequence

from sqlalchemy.orm import Session

import models
import schemas
from infrastructure.database.repositories.base_repository import BaseRepository


class ExerciseGlobalRepository(BaseRepository[models.Exercise_global, schemas.Exercise_global_Create, schemas.Exercise_global_Base]):
    """
    Repository for Exercise_global entity operations.

    Provides methods for global exercise template CRUD operations
    and specific domain queries.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize the Exercise Global repository.

        Args:
            db: The database session
        """
        super().__init__(models.Exercise_global, db)

    def get_by_id(self, exercise_id: int) -> models.Exercise_global | None:
        """
        Retrieve a global exercise by its ID.

        Args:
            exercise_id: The exercise's primary key

        Returns:
            The Exercise_global instance if found, None otherwise
        """
        return self.db.query(models.Exercise_global).filter(
            models.Exercise_global.exercise_id == exercise_id
        ).first()

    def get_by_rutine_id(self, rutine_id: int) -> Sequence[models.Exercise_global]:
        """
        Retrieve all global exercises for a specific routine.

        Args:
            rutine_id: The routine's ID

        Returns:
            List of Exercise_global instances
        """
        return self.db.query(models.Exercise_global).filter(
            models.Exercise_global.rutine_id == rutine_id
        ).all()

    def get_by_name(self, exercise_name: str) -> Sequence[models.Exercise_global]:
        """
        Retrieve global exercises by name.

        Args:
            exercise_name: The exercise name

        Returns:
            List of Exercise_global instances matching the name
        """
        return self.db.query(models.Exercise_global).filter(
            models.Exercise_global.exercise_name == exercise_name
        ).all()

    def get_by_name_and_rutine(
        self,
        exercise_name: str,
        rutine_id: int
    ) -> models.Exercise_global | None:
        """
        Retrieve a global exercise by name within a specific routine.

        Args:
            exercise_name: The exercise name
            rutine_id: The routine's ID

        Returns:
            The Exercise_global instance if found, None otherwise
        """
        return self.db.query(models.Exercise_global).filter(
            models.Exercise_global.exercise_name == exercise_name,
            models.Exercise_global.rutine_id == rutine_id
        ).first()

    def get_by_type(self, exercise_type: str) -> Sequence[models.Exercise_global]:
        """
        Retrieve global exercises by type.

        Args:
            exercise_type: The exercise type

        Returns:
            List of Exercise_global instances matching the type
        """
        return self.db.query(models.Exercise_global).filter(
            models.Exercise_global.exercise_type == exercise_type
        ).all()

    def get_by_group(self, exercise_group: str) -> Sequence[models.Exercise_global]:
        """
        Retrieve global exercises by group.

        Args:
            exercise_group: The exercise group

        Returns:
            List of Exercise_global instances matching the group
        """
        return self.db.query(models.Exercise_global).filter(
            models.Exercise_global.exercise_group == exercise_group
        ).all()

    def create(self, exercise: schemas.Exercise_global_Create) -> models.Exercise_global:
        """
        Create a new global exercise.

        Args:
            exercise: The exercise creation schema

        Returns:
            The created Exercise_global instance
        """
        db_exercise = models.Exercise_global(
            exercise_name=exercise.exercise_name,
            rep=exercise.rep,
            exercise_type=exercise.exercise_type,
            exercise_group=exercise.exercise_group,
            rutine_id=exercise.rutine_id,
            image=exercise.image if exercise.image else 'empty'
        )
        self.db.add(db_exercise)
        self.db.commit()
        self.db.refresh(db_exercise)
        return db_exercise

    def create_from_dict(self, exercise_data: dict, rutine_id: int) -> models.Exercise_global:
        """
        Create a new global exercise from dictionary data.

        Args:
            exercise_data: Dictionary with exercise data
            rutine_id: The parent routine ID

        Returns:
            The created Exercise_global instance
        """
        db_exercise = models.Exercise_global(
            exercise_name=exercise_data.get('exercise_name'),
            rep=exercise_data.get('rep'),
            exercise_type=exercise_data.get('exercise_type'),
            exercise_group=exercise_data.get('exercise_group'),
            rutine_id=rutine_id,
            image=exercise_data.get('image', 'empty')
        )
        self.db.add(db_exercise)
        self.db.commit()
        self.db.refresh(db_exercise)
        return db_exercise

    def exists_in_rutine(self, rutine_id: int, exercise_name: str) -> bool:
        """
        Check if an exercise with the given name exists in the routine.

        Args:
            rutine_id: The routine's ID
            exercise_name: The exercise name to check

        Returns:
            True if exercise exists, False otherwise
        """
        return self.get_by_name_and_rutine(exercise_name, rutine_id) is not None

    def delete(self, exercise_id: int) -> bool:
        """
        Delete a global exercise by ID.

        Args:
            exercise_id: The exercise's primary key

        Returns:
            True if deleted, False if not found
        """
        exercise = self.get_by_id(exercise_id)
        if exercise:
            self.db.delete(exercise)
            self.db.commit()
            return True
        return False

    def delete_by_rutine(self, rutine_id: int) -> int:
        """
        Delete all global exercises for a routine.

        Args:
            rutine_id: The routine's ID

        Returns:
            Number of exercises deleted
        """
        result = self.db.query(models.Exercise_global).filter(
            models.Exercise_global.rutine_id == rutine_id
        ).delete()
        self.db.commit()
        return result

    def update(
        self,
        exercise_id: int,
        update_data: dict
    ) -> models.Exercise_global | None:
        """
        Update a global exercise.

        Args:
            exercise_id: The exercise's primary key
            update_data: Dictionary with fields to update

        Returns:
            The updated Exercise_global instance if found, None otherwise
        """
        exercise = self.get_by_id(exercise_id)
        if exercise:
            for field, value in update_data.items():
                if hasattr(exercise, field) and value is not None:
                    setattr(exercise, field, value)
            self.db.add(exercise)
            self.db.commit()
            self.db.refresh(exercise)
            return exercise
        return None

    def count_by_rutine(self, rutine_id: int) -> int:
        """
        Count global exercises in a routine.

        Args:
            rutine_id: The routine's ID

        Returns:
            Number of exercises in the routine
        """
        return self.db.query(models.Exercise_global).filter(
            models.Exercise_global.rutine_id == rutine_id
        ).count()

    def bulk_create(
        self,
        exercises: list[schemas.Exercise_global_Create]
    ) -> list[models.Exercise_global]:
        """
        Create multiple global exercises at once.

        Args:
            exercises: List of exercise creation schemas

        Returns:
            List of created Exercise_global instances
        """
        db_exercises = []
        for exercise in exercises:
            db_exercise = models.Exercise_global(
                exercise_name=exercise.exercise_name,
                rep=exercise.rep,
                exercise_type=exercise.exercise_type,
                exercise_group=exercise.exercise_group,
                rutine_id=exercise.rutine_id,
                image=exercise.image if exercise.image else 'empty'
            )
            self.db.add(db_exercise)
            db_exercises.append(db_exercise)

        self.db.commit()

        for db_exercise in db_exercises:
            self.db.refresh(db_exercise)

        return db_exercises

    def search_by_type_and_group(
        self,
        exercise_type: str | None = None,
        exercise_group: str | None = None
    ) -> Sequence[models.Exercise_global]:
        """
        Search global exercises by type and/or group.

        Args:
            exercise_type: Optional filter by type
            exercise_group: Optional filter by group

        Returns:
            List of matching Exercise_global instances
        """
        query = self.db.query(models.Exercise_global)

        if exercise_type:
            query = query.filter(
                models.Exercise_global.exercise_type == exercise_type
            )

        if exercise_group:
            query = query.filter(
                models.Exercise_global.exercise_group == exercise_group
            )

        return query.all()
