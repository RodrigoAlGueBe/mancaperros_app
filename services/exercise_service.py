from sqlalchemy.orm import Session

import crud
import models
import schemas


class ExerciseService:

    @staticmethod
    def create_exercise_plan_global(
        db: Session,
        email: str,
        exercise_plan: schemas.Exercise_plan_global_Create
    ) -> models.Exercise_plan_global:
        user: models.User | None = crud.get_user_by_email(db, user_email=email)
        if not user:
            raise ValueError("User not found")

        existing: models.Exercise_plan_global | None = db.query(models.Exercise_plan_global).filter(
            models.Exercise_plan_global.exercise_plan_name == exercise_plan.exercise_plan_name
        ).first()
        if existing:
            raise ValueError("Exercise plan already exists")

        return crud.create_exercise_plan_global(db=db, exercise_plan=exercise_plan, user_id=user.user_id)

    @staticmethod
    def create_routine_global(
        db: Session,
        email: str,
        routine: schemas.Rutine_global_Create
    ) -> models.Rutine_global:
        user: models.User | None = crud.get_user_by_email(db, user_email=email)
        if not user:
            raise ValueError("User not found")

        exercise_plan: models.Exercise_plan_global | None = db.query(models.Exercise_plan_global).filter(
            models.Exercise_plan_global.exercise_plan_id == routine.exercise_plan_id
        ).first()
        if not exercise_plan:
            raise LookupError("Exercise plan not found")

        existing: models.Rutine_global | None = db.query(models.Rutine_global).filter(
            models.Rutine_global.rutine_name == routine.rutine_name,
            models.Rutine_global.exercise_plan_id == routine.exercise_plan_id
        ).first()
        if existing:
            raise ValueError("Routine name already exists for this exercise plan")

        return crud.create_routine_global(db=db, rutine_gobal=routine)

    @staticmethod
    def create_exercise_global(
        db: Session,
        email: str,
        exercise: schemas.Exercise_global_Create
    ) -> models.Exercise_global:
        user: models.User | None = crud.get_user_by_email(db, user_email=email)
        if not user:
            raise ValueError("User not found")

        routine: models.Rutine_global | None = db.query(models.Rutine_global).filter(
            models.Rutine_global.rutine_id == exercise.rutine_id
        ).first()
        if not routine:
            raise LookupError("Routine not found")

        exercise_plan: models.Exercise_plan_global | None = db.query(models.Exercise_plan_global).filter(
            models.Exercise_plan_global.exercise_plan_id == routine.exercise_plan_id
        ).first()
        if not exercise_plan:
            raise LookupError("Exercise plan not found")

        existing: models.Exercise_global | None = db.query(models.Exercise_global).filter(
            models.Exercise_global.rutine_id == routine.rutine_id,
            models.Exercise_global.exercise_name == exercise.exercise_name
        ).first()
        if existing:
            raise ValueError("Exercise name already exists for this Routine")

        return crud.create_exercise_global(db=db, exercise_global=exercise)
