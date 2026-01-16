"""
Exercise plan global endpoints.

This module contains endpoints for exercise plan global operations including:
- Creating exercise plans
- Getting available exercise plans
- Assigning exercise plans to users
- Managing exercise plan muscular groups
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.api.v1.dependencies import get_db, get_current_user, DbSession, CurrentUser
import crud
import models
import schemas


router = APIRouter(prefix="/exercises", tags=["Exercise Plans"])


@router.post("/plans_global", response_model=schemas.Exercise_plan_global_Response)
async def create_exercise_plan_global(
    current_user: CurrentUser,
    exercise_plan: schemas.Exercise_plan_global_Create,
    db: DbSession
):
    """
    Create a new global exercise plan.

    Args:
        current_user: Current authenticated user from token
        exercise_plan: Exercise plan creation data
        db: Database session

    Returns:
        The created exercise plan

    Raises:
        HTTPException: 400 if user not found or plan already exists
    """
    user_from_email = crud.get_user_by_email(db, user_email=current_user.username)
    if not user_from_email:
        raise HTTPException(status_code=400, detail="User not found")

    if db.query(models.Exercise_plan_global).filter(
        models.Exercise_plan_global.exercise_plan_name == exercise_plan.exercise_plan_name
    ).first():
        raise HTTPException(
            status_code=400,
            detail="Exercise plan already exists"
        )

    return crud.create_exercise_plan_global(
        db=db,
        exercise_plan=exercise_plan,
        user_id=user_from_email.user_id
    )


@router.post("/plans_global_full")
async def create_exercise_plan_global_full(
    current_user: CurrentUser,
    exercise_plan_global_full_dict: dict,
    db: DbSession
):
    """
    Create a complete exercise plan global with routines and exercises.

    This endpoint creates an exercise plan along with all its routines
    and exercises in a single request.

    Args:
        current_user: Current authenticated user from token
        exercise_plan_global_full_dict: Complete exercise plan data including routines and exercises
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: 400 if user not found
    """
    user_from_email = crud.get_user_by_email(db, user_email=current_user.username)
    if not user_from_email:
        raise HTTPException(status_code=400, detail='User not found')

    # Create the global exercise plan
    exercise_plan_global = schemas.Exercise_plan_global_Create(
        exercise_plan_name=exercise_plan_global_full_dict['exercise_plan_name'],
        exercise_plan_type=exercise_plan_global_full_dict['exercise_plan_type'],
        difficult_level=exercise_plan_global_full_dict['difficult_level']
    )

    exercise_plan_global = crud.create_exercise_plan_global(
        db=db,
        exercise_plan=exercise_plan_global,
        user_id=user_from_email.user_id
    )

    # Create global routines
    for rutine in exercise_plan_global_full_dict['rutines']:
        rutine_global = schemas.Rutine_global_Create(
            rutine_name=rutine['rutine_name'],
            rutine_type=exercise_plan_global.exercise_plan_type,
            rutine_group=rutine['rutine_group'],
            rutine_category=rutine['rutine_category'],
            exercise_plan_id=exercise_plan_global.exercise_plan_id,
            rst_btw_exercises=rutine['rst_btw_exercises'],
            rst_btw_rounds=rutine['rst_btw_rounds'],
            difficult_level=rutine['difficult_level'],
            rounds=rutine['rounds'],
        )

        rutine_global = crud.create_routine_global(db=db, rutine_gobal=rutine_global)

        for exercise in rutine['exercises']:
            exercise_global = schemas.Exercise_global_Create(
                exercise_name=exercise['exercise_name'],
                rep=exercise['rep'],
                exercise_type=exercise['exercise_type'],
                exercise_group=rutine_global.rutine_group,
                rutine_id=rutine_global.rutine_id,
                image=exercise['image']
            )

            crud.create_exercise_global(db=db, exercise_global=exercise_global)

    return {"detail": "Entire exercise plan created correctly"}


@router.get("/available/{exercise_plan_type}", response_model=List[schemas.Exercise_plan_global_Response])
def get_available_exercise_plans(
    exercise_plan_type: str,
    current_user: CurrentUser,
    db: DbSession
):
    """
    Get available exercise plans by type.

    Args:
        exercise_plan_type: Type of exercise plan to filter by
        current_user: Current authenticated user from token
        db: Database session

    Returns:
        List of available exercise plans of the specified type

    Raises:
        HTTPException: 404 if no exercise plans found
    """
    exercise_plans = db.query(models.Exercise_plan_global).filter(
        models.Exercise_plan_global.exercise_plan_type == exercise_plan_type
    ).all()

    if not exercise_plans:
        raise HTTPException(
            status_code=404,
            detail="No exercise plans found"
        )

    return exercise_plans


@router.put("/assign", response_model=schemas.User_tracker_exercise_plan)
def assign_exercise_plan_to_user(
    current_user: CurrentUser,
    exercise_plan: schemas.Exercise_plan_global_info,
    db: DbSession
):
    """
    Assign a global exercise plan to the current user.

    If the user already has an exercise plan, it will be deleted and
    replaced with the new one. Records are created for tracking purposes.

    Args:
        current_user: Current authenticated user from token
        exercise_plan: Exercise plan info containing the plan ID
        db: Database session

    Returns:
        User tracker record for the assigned exercise plan

    Raises:
        HTTPException: 400 if user or exercise plan not found
    """
    user_from_email = crud.get_user_by_email(db, user_email=current_user.username)
    if not user_from_email:
        raise HTTPException(status_code=400, detail="User not found")

    # Get exercise plan with routines
    exercise_plan_global = db.query(models.Exercise_plan_global)\
        .options(joinedload(models.Exercise_plan_global.rutines))\
        .filter(models.Exercise_plan_global.exercise_plan_id == exercise_plan.exercise_plan_id)\
        .first()

    # Delete existing exercise plan if any
    if db.query(models.Exercise_plan).filter(
        models.Exercise_plan.user_owner_id == user_from_email.user_id
    ).first():
        crud.delete_exercise_plan_for_user(db, user_from_email.user_id)
        crud.record_end_exercise_plan(db, user_from_email.user_id, exercise_plan_global)

    if not exercise_plan_global:
        raise HTTPException(
            status_code=400,
            detail="Exercise plan not found"
        )

    # Assign exercise plan to user
    crud.asign_exercise_plan(
        db=db,
        exercise_plan=exercise_plan_global,
        user_id=user_from_email.user_id
    )

    # Create record of exercise plan start
    response = crud.record_start_exercise_plan(
        db,
        user_from_email.user_id,
        exercise_plan_global
    )

    return {
        "user_id": response.user_id,
        "user_tracker_id": response.user_tracker_id,
        "info_type": response.info_type,
        "record_datetime": response.record_datetime
    }


@router.get("/muscular_groups/{exercise_plan_name}")
def get_muscular_groups_for_exercise_plans(
    exercise_plan_name: str,
    current_user: CurrentUser,
    db: DbSession
):
    """
    Get muscular groups for the user's exercise plan.

    Note: exercise_plan_name parameter is kept for backwards compatibility
    but not used in the current implementation.

    Args:
        exercise_plan_name: Exercise plan name (currently unused)
        current_user: Current authenticated user from token
        db: Database session

    Returns:
        List of routine groups with their IDs

    Raises:
        HTTPException: 400 if user not found
    """
    user_by_email = crud.get_user_by_email(db, user_email=current_user.username)
    if not user_by_email:
        raise HTTPException(status_code=400, detail="User not found")

    exercise_plan = db.query(models.Exercise_plan).filter(
        models.Exercise_plan.user_owner_id == user_by_email.user_id
    ).first()

    routines = db.query(models.Rutine).filter(
        models.Rutine.exercise_plan_id == exercise_plan.exercise_plan_id
    ).all()

    routine_groups = list({
        "rutine_group": routine.rutine_group,
        "rutine_id": routine.rutine_id
    } for routine in routines)

    return routine_groups
