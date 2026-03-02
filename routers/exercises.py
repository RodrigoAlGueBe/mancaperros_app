from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated

import models
import schemas
from core.dependencies import get_db, get_current_user
from services.exercise_service import ExerciseService

router = APIRouter(
    tags=["Exercises"],
)


@router.post("/users/exercise_plans_global", response_model=schemas.Exercise_plan_global)
async def create_exercise_plan_global(
    current_user: Annotated[models.User, Depends(get_current_user)],
    exercise_plan: schemas.Exercise_plan_global_Create,
    db: Session = Depends(get_db)
):
    try:
        return ExerciseService.create_exercise_plan_global(
            db=db, email=current_user.username, exercise_plan=exercise_plan
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/users/exercise_plans_global/routines_global", response_model=schemas.Rutine)
def create_routine_for_exercise_plan(
    current_user: Annotated[models.User, Depends(get_current_user)],
    routine: schemas.Rutine_global_Create,
    db: Session = Depends(get_db)
):
    try:
        return ExerciseService.create_routine_global(
            db=db, email=current_user.username, routine=routine
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/users/exercise_plans_global/routines_global/exercises_global", response_model=schemas.Exercise_global)
def create_exercise_for_routine(
    current_user: Annotated[models.User, Depends(get_current_user)],
    exercise: schemas.Exercise_global_Create,
    db: Session = Depends(get_db)
):
    try:
        return ExerciseService.create_exercise_global(
            db=db, email=current_user.username, exercise=exercise
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
