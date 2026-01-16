"""
Exercise Repository implementation.

This module provides data access operations for Exercise entities,
encapsulating all exercise-related database queries.
"""

from typing import Sequence

from sqlalchemy.orm import Session

import models
import schemas
from infrastructure.database.repositories.base_repository import BaseRepository


class ExerciseRepository(BaseRepository[models.Exercise, schemas.Exercise_Create, schemas.Exercise_Base]):
    """
    Repository for Exercise entity operations.

    Provides methods for exercise CRUD operations and
    specific domain queries.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize the Exercise repository.

        Args:
            db: The database session
        """
        super().__init__(models.Exercise, db)

    def get_by_id(self, exercise_id: int) -> models.Exercise | None:
        """
        Retrieve an exercise by its ID.

        Args:
            exercise_id: The exercise's primary key

        Returns:
            The Exercise instance if found, None otherwise
        """
        return self.db.query(models.Exercise).filter(
            models.Exercise.exercise_id == exercise_id
        ).first()

    def get_by_rutine_id(
        self,
        rutine_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[models.Exercise]:
        """
        Retrieve all exercises for a specific routine with pagination.

        Args:
            rutine_id: The routine's ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Exercise instances
        """
        return self.db.query(models.Exercise).filter(
            models.Exercise.rutine_id == rutine_id
        ).offset(skip).limit(limit).all()

    def get_by_type(
        self,
        exercise_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[models.Exercise]:
        """
        Retrieve exercises by type with pagination.

        Args:
            exercise_type: The exercise type (e.g., "push", "pull")
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Exercise instances matching the type
        """
        return self.db.query(models.Exercise).filter(
            models.Exercise.exercise_type == exercise_type
        ).offset(skip).limit(limit).all()

    def get_by_group(
        self,
        exercise_group: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[models.Exercise]:
        """
        Retrieve exercises by group with pagination.

        Args:
            exercise_group: The exercise group
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Exercise instances matching the group
        """
        return self.db.query(models.Exercise).filter(
            models.Exercise.exercise_group == exercise_group
        ).offset(skip).limit(limit).all()

    def get_by_name(
        self,
        exercise_name: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[models.Exercise]:
        """
        Retrieve exercises by name with pagination.

        Args:
            exercise_name: The exercise name
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Exercise instances matching the name
        """
        return self.db.query(models.Exercise).filter(
            models.Exercise.exercise_name == exercise_name
        ).offset(skip).limit(limit).all()

    def create(self, exercise: schemas.Exercise_Create, rutine_id: int) -> models.Exercise:
        """
        Create a new exercise.

        Args:
            exercise: The exercise creation schema
            rutine_id: The parent routine ID

        Returns:
            The created Exercise instance
        """
        db_exercise = models.Exercise(
            exercise_name=exercise.exercise_name,
            rep=exercise.rep,
            exercise_type=exercise.exercise_type,
            exercise_group=exercise.exercise_group,
            rutine_id=rutine_id,
            image=getattr(exercise, 'image', 'empty')
        )
        self.db.add(db_exercise)
        self.db.commit()
        self.db.refresh(db_exercise)
        return db_exercise

    def create_from_dict(self, exercise_data: dict, rutine_id: int) -> models.Exercise:
        """
        Create a new exercise from dictionary data.

        Args:
            exercise_data: Dictionary with exercise data
            rutine_id: The parent routine ID

        Returns:
            The created Exercise instance
        """
        db_exercise = models.Exercise(
            exercise_name=exercise_data.get('exercise_name', 'New exercise name'),
            rep=exercise_data.get('rep', 'empty'),
            exercise_type=exercise_data.get('exercise_type', 'New exercise type'),
            exercise_group=exercise_data.get('exercise_group', 'New exercise group'),
            rutine_id=rutine_id,
            image=exercise_data.get('image', 'empty')
        )
        self.db.add(db_exercise)
        self.db.commit()
        self.db.refresh(db_exercise)
        return db_exercise

    def update(self, exercise: models.Exercise) -> models.Exercise:
        """
        Update an existing exercise.

        Args:
            exercise: The exercise instance with updated values

        Returns:
            The updated Exercise instance
        """
        self.db.add(exercise)
        self.db.commit()
        self.db.refresh(exercise)
        return exercise

    def update_reps(self, exercise_id: int, new_reps: str) -> models.Exercise | None:
        """
        Update the reps for an exercise.

        Args:
            exercise_id: The exercise's primary key
            new_reps: The new reps value

        Returns:
            The updated Exercise instance if found, None otherwise
        """
        exercise = self.get_by_id(exercise_id)
        if exercise:
            exercise.rep = new_reps
            self.db.add(exercise)
            self.db.commit()
            self.db.refresh(exercise)
            return exercise
        return None

    def update_image(self, exercise_id: int, image_path: str) -> models.Exercise | None:
        """
        Update the image for an exercise.

        Args:
            exercise_id: The exercise's primary key
            image_path: The new image path

        Returns:
            The updated Exercise instance if found, None otherwise
        """
        exercise = self.get_by_id(exercise_id)
        if exercise:
            exercise.image = image_path
            self.db.add(exercise)
            self.db.commit()
            self.db.refresh(exercise)
            return exercise
        return None

    def delete(self, exercise_id: int) -> bool:
        """
        Delete an exercise by ID.

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
        Delete all exercises for a routine.

        Args:
            rutine_id: The routine's ID

        Returns:
            Number of exercises deleted
        """
        result = self.db.query(models.Exercise).filter(
            models.Exercise.rutine_id == rutine_id
        ).delete()
        self.db.commit()
        return result

    def count_by_rutine(self, rutine_id: int) -> int:
        """
        Count exercises in a routine.

        Args:
            rutine_id: The routine's ID

        Returns:
            Number of exercises in the routine
        """
        return self.db.query(models.Exercise).filter(
            models.Exercise.rutine_id == rutine_id
        ).count()

    def exists_in_rutine(self, rutine_id: int, exercise_name: str) -> bool:
        """
        Check if an exercise with the given name exists in the routine.

        Args:
            rutine_id: The routine's ID
            exercise_name: The exercise name to check

        Returns:
            True if exercise exists, False otherwise
        """
        return self.db.query(models.Exercise).filter(
            models.Exercise.rutine_id == rutine_id,
            models.Exercise.exercise_name == exercise_name
        ).first() is not None

    def bulk_update_reps(
        self,
        exercises: list[models.Exercise],
        reps_updates: dict[int, str]
    ) -> list[models.Exercise]:
        """
        Bulk update reps for multiple exercises.

        Args:
            exercises: List of exercise instances
            reps_updates: Dictionary mapping exercise_id to new reps

        Returns:
            List of updated Exercise instances
        """
        for exercise in exercises:
            if exercise.exercise_id in reps_updates:
                exercise.rep = reps_updates[exercise.exercise_id]
                self.db.add(exercise)

        self.db.commit()

        for exercise in exercises:
            self.db.refresh(exercise)

        return exercises
