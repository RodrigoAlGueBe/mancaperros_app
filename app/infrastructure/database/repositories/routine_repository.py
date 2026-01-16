"""
Routine Repository - Repository for Routine and Exercise entities.

This module encapsulates all database operations related to Routine, RoutineGlobal,
Exercise, and ExerciseGlobal entities.
"""

from typing import Optional, List, Any, Dict

from sqlalchemy.orm import Session, joinedload

from .base_repository import BaseRepository

# Import models
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
import models


class RoutineRepository(BaseRepository[models.Rutine, Any, Any]):
    """
    Repository for Rutine (user-assigned) entity operations.

    Handles operations for routines that belong to user-assigned exercise plans.
    """

    def __init__(self, db: Session):
        """
        Initialize the RoutineRepository.

        Args:
            db: The database session
        """
        super().__init__(models.Rutine, db)

    def get_by_id(self, routine_id: int) -> Optional[models.Rutine]:
        """
        Retrieve a routine by its ID.

        Args:
            routine_id: The routine's primary key

        Returns:
            The Rutine if found, None otherwise
        """
        return self.db.query(models.Rutine).filter(
            models.Rutine.rutine_id == routine_id
        ).first()

    def get_by_id_with_exercises(self, routine_id: int) -> Optional[models.Rutine]:
        """
        Retrieve a routine with its exercises eagerly loaded.

        Args:
            routine_id: The routine's primary key

        Returns:
            The Rutine with loaded exercises if found, None otherwise
        """
        return self.db.query(models.Rutine).options(
            joinedload(models.Rutine.exercises)
        ).filter(
            models.Rutine.rutine_id == routine_id
        ).first()

    def get_by_exercise_plan_id(self, exercise_plan_id: int) -> List[models.Rutine]:
        """
        Retrieve all routines for a specific exercise plan.

        Args:
            exercise_plan_id: The exercise plan's ID

        Returns:
            List of Rutine entities
        """
        return self.db.query(models.Rutine).filter(
            models.Rutine.exercise_plan_id == exercise_plan_id
        ).all()

    def get_by_exercise_plan_and_group(
        self,
        exercise_plan_id: int,
        routine_group: str
    ) -> Optional[models.Rutine]:
        """
        Retrieve a routine by exercise plan and muscle group.

        Args:
            exercise_plan_id: The exercise plan's ID
            routine_group: The routine's muscle group

        Returns:
            The Rutine if found, None otherwise
        """
        return self.db.query(models.Rutine).filter(
            models.Rutine.exercise_plan_id == exercise_plan_id,
            models.Rutine.rutine_group == routine_group
        ).first()

    def create(
        self,
        rutine_name: str,
        rutine_type: str,
        rutine_group: str,
        rutine_category: str,
        exercise_plan_id: int,
        rounds: int = 0,
        rst_btw_exercises: str = "0",
        rst_btw_rounds: str = "0",
        difficult_level: str = "New rutine difficult level"
    ) -> models.Rutine:
        """
        Create a new routine.

        Args:
            rutine_name: Name of the routine
            rutine_type: Type of the routine
            rutine_group: Muscle group
            rutine_category: Category of the routine
            exercise_plan_id: Parent exercise plan ID
            rounds: Number of rounds
            rst_btw_exercises: Rest between exercises
            rst_btw_rounds: Rest between rounds
            difficult_level: Difficulty level

        Returns:
            The created Rutine entity
        """
        db_routine = models.Rutine(
            rutine_name=rutine_name,
            rutine_type=rutine_type,
            rutine_group=rutine_group,
            rutine_category=rutine_category,
            exercise_plan_id=exercise_plan_id,
            rounds=rounds,
            rst_btw_exercises=rst_btw_exercises,
            rst_btw_rounds=rst_btw_rounds,
            difficult_level=difficult_level
        )
        self.db.add(db_routine)
        self.db.commit()
        self.db.refresh(db_routine)
        return db_routine

    def create_without_commit(
        self,
        rutine_name: str,
        rutine_type: str,
        rutine_group: str,
        rutine_category: str,
        exercise_plan_id: int,
        rounds: int = 0,
        rst_btw_exercises: str = "0",
        rst_btw_rounds: str = "0",
        difficult_level: str = "New rutine difficult level"
    ) -> models.Rutine:
        """
        Create a new routine without committing (for transaction batching).

        Args:
            Same as create()

        Returns:
            The created Rutine entity (not committed)
        """
        db_routine = models.Rutine(
            rutine_name=rutine_name,
            rutine_type=rutine_type,
            rutine_group=rutine_group,
            rutine_category=rutine_category,
            exercise_plan_id=exercise_plan_id,
            rounds=rounds,
            rst_btw_exercises=rst_btw_exercises,
            rst_btw_rounds=rst_btw_rounds,
            difficult_level=difficult_level
        )
        self.db.add(db_routine)
        self.db.flush()
        return db_routine

    def update(self, routine: models.Rutine) -> models.Rutine:
        """
        Update an existing routine.

        Args:
            routine: The routine entity with updated values

        Returns:
            The updated Rutine entity
        """
        self.db.add(routine)
        self.db.commit()
        self.db.refresh(routine)
        return routine

    def delete_by_exercise_plan_id(self, exercise_plan_id: int) -> int:
        """
        Delete all routines for a specific exercise plan.

        Args:
            exercise_plan_id: The exercise plan's ID

        Returns:
            Number of deleted routines
        """
        deleted_count = self.db.query(models.Rutine).filter(
            models.Rutine.exercise_plan_id == exercise_plan_id
        ).delete()
        self.db.commit()
        return deleted_count

    def get_routine_groups_by_exercise_plan(
        self,
        exercise_plan_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get all routine groups for an exercise plan.

        Args:
            exercise_plan_id: The exercise plan's ID

        Returns:
            List of dictionaries with rutine_group and rutine_id
        """
        routines = self.get_by_exercise_plan_id(exercise_plan_id)
        return [
            {"rutine_group": routine.rutine_group, "rutine_id": routine.rutine_id}
            for routine in routines
        ]


class RoutineGlobalRepository(BaseRepository[models.Rutine_global, Any, Any]):
    """
    Repository for Rutine_global (template) entity operations.

    Handles operations for global routine templates.
    """

    def __init__(self, db: Session):
        """
        Initialize the RoutineGlobalRepository.

        Args:
            db: The database session
        """
        super().__init__(models.Rutine_global, db)

    def get_by_id(self, routine_id: int) -> Optional[models.Rutine_global]:
        """
        Retrieve a global routine by its ID.

        Args:
            routine_id: The routine's primary key

        Returns:
            The Rutine_global if found, None otherwise
        """
        return self.db.query(models.Rutine_global).filter(
            models.Rutine_global.rutine_id == routine_id
        ).first()

    def get_by_exercise_plan_id(
        self,
        exercise_plan_id: int
    ) -> List[models.Rutine_global]:
        """
        Retrieve all global routines for a specific exercise plan.

        Args:
            exercise_plan_id: The exercise plan's ID

        Returns:
            List of Rutine_global entities
        """
        return self.db.query(models.Rutine_global).filter(
            models.Rutine_global.exercise_plan_id == exercise_plan_id
        ).all()

    def get_by_name_and_plan(
        self,
        name: str,
        exercise_plan_id: int
    ) -> Optional[models.Rutine_global]:
        """
        Retrieve a global routine by name within a specific exercise plan.

        Args:
            name: The routine name
            exercise_plan_id: The exercise plan's ID

        Returns:
            The Rutine_global if found, None otherwise
        """
        return self.db.query(models.Rutine_global).filter(
            models.Rutine_global.rutine_name == name,
            models.Rutine_global.exercise_plan_id == exercise_plan_id
        ).first()

    def create(
        self,
        rutine_name: str,
        rutine_type: str,
        rutine_group: str,
        rutine_category: str,
        exercise_plan_id: int,
        rounds: int = 0,
        rst_btw_exercises: str = "0",
        rst_btw_rounds: str = "0",
        difficult_level: str = "New rutine difficult level"
    ) -> models.Rutine_global:
        """
        Create a new global routine.

        Args:
            rutine_name: Name of the routine
            rutine_type: Type of the routine
            rutine_group: Muscle group
            rutine_category: Category of the routine
            exercise_plan_id: Parent exercise plan ID
            rounds: Number of rounds
            rst_btw_exercises: Rest between exercises
            rst_btw_rounds: Rest between rounds
            difficult_level: Difficulty level

        Returns:
            The created Rutine_global entity
        """
        db_routine = models.Rutine_global(
            rutine_name=rutine_name,
            rutine_type=rutine_type,
            rutine_group=rutine_group,
            rutine_category=rutine_category,
            exercise_plan_id=exercise_plan_id,
            rounds=rounds,
            rst_btw_exercises=rst_btw_exercises,
            rst_btw_rounds=rst_btw_rounds,
            difficult_level=difficult_level
        )
        self.db.add(db_routine)
        self.db.commit()
        self.db.refresh(db_routine)
        return db_routine

    def create_from_schema(self, routine_schema: Any) -> models.Rutine_global:
        """
        Create a new global routine from a Pydantic schema.

        Args:
            routine_schema: The routine creation schema

        Returns:
            The created Rutine_global entity
        """
        db_routine = models.Rutine_global(**routine_schema.dict())
        self.db.add(db_routine)
        self.db.commit()
        self.db.refresh(db_routine)
        return db_routine

    def exists_by_name_in_plan(self, name: str, exercise_plan_id: int) -> bool:
        """
        Check if a routine name exists within a specific exercise plan.

        Args:
            name: The routine name
            exercise_plan_id: The exercise plan's ID

        Returns:
            True if the routine name exists in that plan
        """
        return self.get_by_name_and_plan(name, exercise_plan_id) is not None


class ExerciseRepository(BaseRepository[models.Exercise, Any, Any]):
    """
    Repository for Exsercise (user-assigned) entity operations.

    Handles operations for exercises that belong to user-assigned routines.
    """

    def __init__(self, db: Session):
        """
        Initialize the ExerciseRepository.

        Args:
            db: The database session
        """
        super().__init__(models.Exercise, db)

    def get_by_id(self, exercise_id: int) -> Optional[models.Exercise]:
        """
        Retrieve an exercise by its ID.

        Args:
            exercise_id: The exercise's primary key

        Returns:
            The Exsercise if found, None otherwise
        """
        return self.db.query(models.Exercise).filter(
            models.Exercise.exercise_id == exercise_id
        ).first()

    def get_by_routine_id(self, routine_id: int) -> List[models.Exercise]:
        """
        Retrieve all exercises for a specific routine.

        Args:
            routine_id: The routine's ID

        Returns:
            List of Exsercise entities
        """
        return self.db.query(models.Exercise).filter(
            models.Exercise.rutine_id == routine_id
        ).all()

    def create(
        self,
        exercise_name: str,
        rep: str,
        exercise_type: str,
        exercise_group: str,
        rutine_id: int,
        image: str = "empty"
    ) -> models.Exercise:
        """
        Create a new exercise.

        Args:
            exercise_name: Name of the exercise
            rep: Number of repetitions
            exercise_type: Type of exercise
            exercise_group: Muscle group
            rutine_id: Parent routine ID
            image: Exercise image path

        Returns:
            The created Exsercise entity
        """
        db_exercise = models.Exercise(
            exercise_name=exercise_name,
            rep=rep,
            exercise_type=exercise_type,
            exercise_group=exercise_group,
            rutine_id=rutine_id,
            image=image
        )
        self.db.add(db_exercise)
        self.db.commit()
        self.db.refresh(db_exercise)
        return db_exercise

    def create_from_schema(
        self,
        exercise_schema: Any,
        routine_id: int
    ) -> models.Exercise:
        """
        Create a new exercise from a Pydantic schema.

        Args:
            exercise_schema: The exercise creation schema
            routine_id: Parent routine ID

        Returns:
            The created Exsercise entity
        """
        db_exercise = models.Exercise(
            **exercise_schema.dict(),
            rutine_id=routine_id
        )
        self.db.add(db_exercise)
        self.db.commit()
        self.db.refresh(db_exercise)
        return db_exercise

    def update_reps(self, exercise: models.Exercise, new_reps: str) -> models.Exercise:
        """
        Update an exercise's repetitions.

        Args:
            exercise: The exercise entity
            new_reps: New repetition value

        Returns:
            The updated Exsercise entity
        """
        exercise.rep = new_reps
        self.db.add(exercise)
        self.db.commit()
        self.db.refresh(exercise)
        return exercise

    def delete_by_routine_id(self, routine_id: int) -> int:
        """
        Delete all exercises for a specific routine.

        Args:
            routine_id: The routine's ID

        Returns:
            Number of deleted exercises
        """
        deleted_count = self.db.query(models.Exercise).filter(
            models.Exercise.rutine_id == routine_id
        ).delete()
        self.db.commit()
        return deleted_count


class ExerciseGlobalRepository(BaseRepository[models.Exercise_global, Any, Any]):
    """
    Repository for Exsercise_global (template) entity operations.

    Handles operations for global exercise templates.
    """

    def __init__(self, db: Session):
        """
        Initialize the ExerciseGlobalRepository.

        Args:
            db: The database session
        """
        super().__init__(models.Exercise_global, db)

    def get_by_id(self, exercise_id: int) -> Optional[models.Exercise_global]:
        """
        Retrieve a global exercise by its ID.

        Args:
            exercise_id: The exercise's primary key

        Returns:
            The Exsercise_global if found, None otherwise
        """
        return self.db.query(models.Exercise_global).filter(
            models.Exercise_global.exercise_id == exercise_id
        ).first()

    def get_by_routine_id(self, routine_id: int) -> List[models.Exercise_global]:
        """
        Retrieve all global exercises for a specific routine.

        Args:
            routine_id: The routine's ID

        Returns:
            List of Exsercise_global entities
        """
        return self.db.query(models.Exercise_global).filter(
            models.Exercise_global.rutine_id == routine_id
        ).all()

    def get_by_name_in_routine(
        self,
        name: str,
        routine_id: int
    ) -> Optional[models.Exercise_global]:
        """
        Retrieve a global exercise by name within a specific routine.

        Args:
            name: The exercise name
            routine_id: The routine's ID

        Returns:
            The Exsercise_global if found, None otherwise
        """
        return self.db.query(models.Exercise_global).filter(
            models.Exercise_global.exercise_name == name,
            models.Exercise_global.rutine_id == routine_id
        ).first()

    def create(
        self,
        exercise_name: str,
        rep: str,
        exercise_type: str,
        exercise_group: str,
        rutine_id: int,
        image: str = "empty"
    ) -> models.Exercise_global:
        """
        Create a new global exercise.

        Args:
            exercise_name: Name of the exercise
            rep: Number of repetitions
            exercise_type: Type of exercise
            exercise_group: Muscle group
            rutine_id: Parent routine ID
            image: Exercise image path

        Returns:
            The created Exsercise_global entity
        """
        db_exercise = models.Exercise_global(
            exercise_name=exercise_name,
            rep=rep,
            exercise_type=exercise_type,
            exercise_group=exercise_group,
            rutine_id=rutine_id,
            image=image
        )
        self.db.add(db_exercise)
        self.db.commit()
        self.db.refresh(db_exercise)
        return db_exercise

    def create_from_schema(self, exercise_schema: Any) -> models.Exercise_global:
        """
        Create a new global exercise from a Pydantic schema.

        Args:
            exercise_schema: The exercise creation schema

        Returns:
            The created Exsercise_global entity
        """
        db_exercise = models.Exercise_global(**exercise_schema.dict())
        self.db.add(db_exercise)
        self.db.commit()
        self.db.refresh(db_exercise)
        return db_exercise

    def exists_by_name_in_routine(self, name: str, routine_id: int) -> bool:
        """
        Check if an exercise name exists within a specific routine.

        Args:
            name: The exercise name
            routine_id: The routine's ID

        Returns:
            True if the exercise name exists in that routine
        """
        return self.get_by_name_in_routine(name, routine_id) is not None
