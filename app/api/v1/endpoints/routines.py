"""
Routine management endpoints.

This module contains endpoints for routine operations including:
- Creating routines for exercise plans
- Getting routines and their exercises
- Ending routines and tracking progress
- Getting next routine recommendations
"""

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.dependencies import get_db, get_current_user, DbSession, CurrentUser
from utils.functions import f_reps_to_seconds
import crud
import models
import schemas


router = APIRouter(prefix="/routines", tags=["Routines"])


@router.post("/global", response_model=schemas.Rutine)
def create_routine_for_exercise_plan(
    current_user: CurrentUser,
    routine: schemas.Rutine_global_Create,
    db: DbSession
):
    """
    Create a new global routine for an exercise plan.

    Args:
        current_user: Current authenticated user from token
        routine: Routine creation data
        db: Database session

    Returns:
        The created routine

    Raises:
        HTTPException: 400 if user not found or routine name already exists
        HTTPException: 404 if exercise plan not found
    """
    user_from_email = crud.get_user_by_email(db, user_email=current_user.username)
    if not user_from_email:
        raise HTTPException(status_code=400, detail="User not found")

    exercise_plan = db.query(models.Exercise_plan_global).filter(
        models.Exercise_plan_global.exercise_plan_id == routine.exercise_plan_id
    ).first()

    if not exercise_plan:
        raise HTTPException(status_code=404, detail="Exercise plan not found")

    if db.query(models.Rutine_global).filter(
        models.Rutine_global.rutine_name == routine.rutine_name,
        models.Rutine_global.exercise_plan_id == routine.exercise_plan_id
    ).first():
        raise HTTPException(
            status_code=400,
            detail="Routine name already exists for this exercise plan"
        )

    return crud.create_routine_global(db=db, rutine_gobal=routine)


@router.post("/global/exercises", response_model=schemas.Exercise_global)
def create_exercise_for_routine(
    current_user: CurrentUser,
    exercise: schemas.Exercise_global_Create,
    db: DbSession
):
    """
    Create a new global exercise for a routine.

    Args:
        current_user: Current authenticated user from token
        exercise: Exercise creation data
        db: Database session

    Returns:
        The created exercise

    Raises:
        HTTPException: 400 if user not found or exercise name already exists
        HTTPException: 404 if routine or exercise plan not found
    """
    user_from_email = crud.get_user_by_email(db, user_email=current_user.username)
    if not user_from_email:
        raise HTTPException(status_code=400, detail="User not found")

    routine = db.query(models.Rutine_global).filter(
        models.Rutine_global.rutine_id == exercise.rutine_id
    ).first()

    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    exercise_plan = db.query(models.Exercise_plan_global).filter(
        models.Exercise_plan_global.exercise_plan_id == routine.exercise_plan_id
    ).first()

    if not exercise_plan:
        raise HTTPException(status_code=404, detail="Exercise plan not found")

    if db.query(models.Exercise_global).filter(
        models.Exercise_plan_global.exercise_plan_id == exercise_plan.exercise_plan_id,
        models.Rutine_global.rutine_id == routine.rutine_id,
        models.Exercise_global.exercise_name == exercise.exercise_name
    ).first():
        raise HTTPException(
            status_code=400,
            detail="Exercise name already exists for this Routine"
        )

    return crud.create_exercise_global(db=db, exercise_global=exercise)


@router.post("/end")
async def end_routine(
    current_user: CurrentUser,
    exercises_summary: dict,
    db: DbSession
):
    """
    End a routine and record the exercise progress.

    Updates exercise repetitions and creates a tracking record
    with increments for different exercise types.

    HIGH-08: This endpoint now uses dual-write mode to record events
    in both the legacy users_tracker table and the new workout_events table.

    Args:
        current_user: Current authenticated user from token
        exercises_summary: Dictionary containing routine_group and exercises data
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: 400 if user not found
        HTTPException: 500 if received routine doesn't match started routine
    """
    user_from_email = crud.get_user_by_email(db, user_email=current_user.username)
    if not user_from_email:
        raise HTTPException(status_code=400, detail="User not found")

    # Get user's last exercise plan
    last_exercise_plan = db.query(models.Exercise_plan).filter(
        models.Exercise_plan.user_owner_id == user_from_email.user_id
    ).first()

    # Get current routine
    last_routine = db.query(models.Rutine).filter(
        models.Rutine.exercise_plan_id == last_exercise_plan.exercise_plan_id,
        models.Rutine.rutine_group == exercises_summary["routine_group"]
    ).first()

    # Update routine exercises
    exercises_received = exercises_summary["exercises"]
    exercise_quantity = len(exercises_received)

    # Verify exercise count matches
    if exercise_quantity != len(last_routine.exercises):
        raise HTTPException(
            status_code=500,
            detail="Received routine does not match with started routine"
        )

    exercise_order_name = "exercise_"
    exercise_sequence = "start"
    exercise_record = {
        "record_datetime": datetime.now(timezone.utc).replace(tzinfo=None),
        "info_type": "rutine_end",
        "info_description": exercises_summary["routine_group"],
        "exercise_increments": {},
        "push_increment": 0,
        "pull_increment": 0,
        "isometric_increment": 0,
    }

    for exercise_db in last_routine.exercises:
        new_reps = exercises_received[exercise_order_name + str(exercise_sequence)]["reps"]
        exercise_record["exercise_increments"][exercise_db.exercise_name] = (
            int(exercise_db.rep) - int(new_reps)
        )
        exercise_db.rep = new_reps

        exercise_type = exercise_db.exercise_type.split('-')

        # Update increments based on exercise type
        if exercise_type[0] == "push":
            exercise_record["push_increment"] += int(exercise_db.rep) - int(new_reps)
        elif exercise_type[0] == "pull":
            exercise_record["pull_increment"] += int(exercise_db.rep) - int(new_reps)
        else:
            exercise_record["isometric_increment"] += (
                int(f_reps_to_seconds(exercise_db.rep)) - int(f_reps_to_seconds(new_reps))
            )

        # Update exercise sequence
        if exercise_sequence == "start":
            exercise_sequence = 2
        elif exercise_sequence == "end":
            break
        elif int(exercise_sequence) < exercise_quantity - 1:
            exercise_sequence += 1
        else:
            exercise_sequence = "end"

    # Update the routine
    crud.update_routine(db, last_routine)

    # HIGH-08: Create end routine record using legacy function
    # This maintains backward compatibility with existing data
    crud.redord_end_rutine(db, user_from_email.user_id, exercise_record)

    # HIGH-08: Also record in new WorkoutEvent table for migration
    # This enables dual-write during the transition period
    try:
        crud.record_routine_completed(
            db=db,
            user_id=user_from_email.user_id,
            routine_group=exercises_summary["routine_group"],
            exercise_increments=exercise_record["exercise_increments"],
            push_increment=exercise_record["push_increment"],
            pull_increment=exercise_record["pull_increment"],
            isometric_increment=exercise_record["isometric_increment"],
        )
    except Exception:
        # If new table doesn't exist yet, silently continue
        # The legacy record was already saved
        pass

    return {"detail": "Routine ended correctly"}


@router.get("/by_exercise_plan/{exercise_plan_id}")
async def get_all_routines_for_exercise_plan(
    exercise_plan_id: int,
    db: DbSession
):
    """
    Get all routines for a specific exercise plan.

    Args:
        exercise_plan_id: ID of the exercise plan
        db: Database session

    Returns:
        List of routines for the exercise plan
    """
    return db.query(models.Rutine).filter(
        models.Rutine.exercise_plan_id == exercise_plan_id
    ).all()


@router.get("/assigned")
async def get_assigned_routines(
    current_user: CurrentUser,
    db: DbSession
):
    """
    Get routines assigned to the current user.

    Args:
        current_user: Current authenticated user from token
        db: Database session

    Returns:
        List of routines from the user's current exercise plan

    Raises:
        HTTPException: 400 if user not found
    """
    user_from_email = crud.get_user_by_email(db, user_email=current_user.username)
    if not user_from_email:
        raise HTTPException(status_code=400, detail="User not found")

    # Get current exercise plan
    assigned_exercise_plan = db.query(models.Exercise_plan).filter(
        models.Exercise_plan.user_owner_id == user_from_email.user_id
    ).first()

    return db.query(models.Rutine).filter(
        models.Rutine.exercise_plan_id == assigned_exercise_plan.exercise_plan_id
    ).all()


@router.get("/{routine_id}/exercises")
async def get_all_exercises_for_routine(
    routine_id: int,
    current_user: CurrentUser,
    db: DbSession
):
    """
    Get all exercises for a specific routine.

    Returns formatted exercise data including routine metadata
    and exercises in a structured format.

    Args:
        routine_id: ID of the routine
        current_user: Current authenticated user from token
        db: Database session

    Returns:
        Dictionary with routine info and exercises

    Raises:
        HTTPException: 404 if routine not found
    """
    if not db.query(models.Rutine).filter(
        models.Rutine.rutine_id == routine_id
    ).first():
        raise HTTPException(status_code=404, detail="Rutine not found")

    routine = db.query(models.Rutine).filter(
        models.Rutine.rutine_id == routine_id
    ).first()

    exercises = db.query(models.Exercise).filter(
        models.Exercise.rutine_id == routine_id
    ).all()

    output_response = {
        "routine_group": routine.rutine_group,
        "rutine_type": routine.rutine_type,
        "rutine_category": routine.rutine_category,
        "num_series": routine.rounds,
        "rest_between_exercises": routine.rst_btw_exercises,
        "rest_between_series": routine.rst_btw_rounds,
        "exercises": {}
    }

    count = 0
    for exercise in exercises:
        count += 1

        if len(output_response["exercises"]) == 0:
            output_response["exercises"]["exercise_start"] = {
                "exercise_name": exercise.exercise_name,
                "image": exercise.image,
                "reps": exercise.rep,
                "exercise_type": exercise.exercise_type,
                "exercise_group": exercise.exercise_group
            }

        elif len(output_response["exercises"]) == len(exercises) - 1:
            output_response["exercises"]["exercise_end"] = {
                "exercise_name": exercise.exercise_name,
                "image": exercise.image,
                "reps": exercise.rep,
                "exercise_type": exercise.exercise_type,
                "exercise_group": exercise.exercise_group
            }

        else:
            output_response["exercises"][f"exercise_{count}"] = {
                "exercise_name": exercise.exercise_name,
                "reps": exercise.rep,
                "exercise_type": exercise.exercise_type,
                "exercise_group": exercise.exercise_group,
                "image": exercise.image
            }

    return output_response


@router.get("/next")
def get_next_routine(
    current_user: CurrentUser,
    db: DbSession
):
    """
    Get the next recommended routine for the user.

    Determines the next routine based on the user's exercise plan
    routine order and their last completed routine.

    This endpoint uses the new WorkoutEvent models with fallback to legacy
    User_Tracker for backward compatibility during migration (HIGH-08).

    Args:
        current_user: Current authenticated user from token
        db: Database session

    Returns:
        Dictionary with next routine name and ID

    Raises:
        HTTPException: 400 if user not found
        HTTPException: 404 if no active exercise plan found
    """
    user_by_email = crud.get_user_by_email(db, user_email=current_user.username)
    if not user_by_email:
        raise HTTPException(status_code=400, detail="User not found")

    active_exercise_plan = db.query(models.Exercise_plan).filter(
        models.Exercise_plan.user_owner_id == user_by_email.user_id
    ).first()

    if not active_exercise_plan:
        raise HTTPException(status_code=404, detail="No active exercise plan found")

    try:
        routine_order = json.loads(active_exercise_plan.routine_group_order)
    except (ValueError, TypeError):
        routine_order = active_exercise_plan.routine_group_order

    # HIGH-08: Try new WorkoutEvent models first, fallback to legacy User_Tracker
    # This allows gradual migration without breaking existing functionality
    last_routine_completion = None
    exercise_plan_start = None
    last_routine_group = None
    last_routine_timestamp = None
    plan_start_timestamp = None

    # Try new polymorphic models first
    try:
        last_routine_completion = db.query(models.RoutineCompletedEvent).filter(
            models.RoutineCompletedEvent.user_id == user_by_email.user_id
        ).order_by(models.RoutineCompletedEvent.timestamp.desc()).first()

        if last_routine_completion:
            last_routine_group = last_routine_completion.routine_group
            last_routine_timestamp = last_routine_completion.timestamp

        exercise_plan_start = db.query(models.ExercisePlanStartedEvent).filter(
            models.ExercisePlanStartedEvent.user_id == user_by_email.user_id
        ).order_by(models.ExercisePlanStartedEvent.timestamp.desc()).first()

        if exercise_plan_start:
            plan_start_timestamp = exercise_plan_start.timestamp
    except Exception:
        # If new models fail (table doesn't exist yet), use None to trigger fallback
        pass

    # Fallback to legacy User_Tracker if new models returned no data
    if last_routine_completion is None or exercise_plan_start is None:
        legacy_last_routine = db.query(models.User_Tracker).filter(
            models.User_Tracker.user_id == user_by_email.user_id,
            models.User_Tracker.info_type == "rutine_end"
        ).order_by(models.User_Tracker.record_datetime.desc()).first()

        legacy_plan_start = db.query(models.User_Tracker).filter(
            models.User_Tracker.user_id == user_by_email.user_id,
            models.User_Tracker.info_type == "exercise_plan_start"
        ).order_by(models.User_Tracker.record_datetime.desc()).first()

        if last_routine_completion is None and legacy_last_routine:
            last_routine_group = legacy_last_routine.info_description
            last_routine_timestamp = legacy_last_routine.record_datetime

        if exercise_plan_start is None and legacy_plan_start:
            plan_start_timestamp = legacy_plan_start.record_datetime

    # Determine next routine based on timestamps
    if plan_start_timestamp and last_routine_timestamp:
        if plan_start_timestamp > last_routine_timestamp:
            # Exercise plan just started, return first routine
            next_routine = routine_order[0] if routine_order else None
        else:
            # Find next routine in order after last completed
            next_routine = _find_next_routine_in_order(routine_order, last_routine_group)
    elif plan_start_timestamp and not last_routine_timestamp:
        # Plan started but no routines completed yet
        next_routine = routine_order[0] if routine_order else None
    elif last_routine_group:
        # Has completed routines, find next
        next_routine = _find_next_routine_in_order(routine_order, last_routine_group)
    else:
        # No history, return first routine
        next_routine = routine_order[0] if routine_order else None

    if not next_routine:
        raise HTTPException(status_code=404, detail="Could not determine next routine")

    # Get routine ID
    routine_record = db.query(models.Rutine).filter(
        models.Rutine.exercise_plan_id == active_exercise_plan.exercise_plan_id,
        models.Rutine.rutine_group == next_routine
    ).first()

    if not routine_record:
        raise HTTPException(status_code=404, detail=f"Routine '{next_routine}' not found")

    return {
        'routine': next_routine,
        'routine_id': routine_record.rutine_id
    }


def _find_next_routine_in_order(routine_order: list, last_routine_group: str) -> str | None:
    """
    Find the next routine in the order after the last completed one.

    Args:
        routine_order: List of routine groups in order
        last_routine_group: The last completed routine group

    Returns:
        The next routine group name, or first routine if at end of cycle
    """
    if not routine_order:
        return None

    for i, muscular_group in enumerate(routine_order):
        if muscular_group == last_routine_group:
            # Return next routine, or wrap to first if at end
            if i + 1 < len(routine_order):
                return routine_order[i + 1]
            else:
                return routine_order[0]

    # If last routine not found in order, return first
    return routine_order[0]
