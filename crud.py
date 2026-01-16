from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import Session
from sqlalchemy import select

from passlib.context import CryptContext
from jose import jwt

import models, schemas


# SECURITY: Removed fake_users_db hardcoded test user (security audit 2026-01-09)
# The hash "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW" corresponds
# to the publicly known password "secret" from FastAPI examples - never use in production.


#********************************* GET METHODS *********************************
#------------------------- User -------------------------
# DEPRECATED: Use UserRepository.get_by_id() instead
def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

# DEPRECATED: Use UserRepository.get_by_username() instead
def get_user_by_username(db: Session, username:str):    #Rod 18/09/2023 documentation get_user -> get_user_by_username
    return db.query(models.User).filter(models.User.user_name == username).first()

#def get_user_by_email(db: Session, user_email: str):    #Rod 20/08/2023 commented
#   return db.query(models.User).filter(models.User.email == user_email).first()    #Rod 20/08/2023 commented
# DEPRECATED: Use UserRepository.get_by_email() instead
def get_user_by_email(db: Session, user_email: str):    #Rod 20/08/2023 add this function
   return db.query(models.User).filter(models.User.email == user_email).first()

# DEPRECATED: Use UserRepository.get_all() instead
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()
#--------------------------------------------------------

#-------------------- Exercise_plan ---------------------
# DEPRECATED: Use ExercisePlanRepository.get_by_id() instead
def get_exercise_plan_info(db: Session, exercise_plan_id: int):
    return db.query(
        models.Exercise_plan
        ).filter(models.Exercise_plan.exercise_plan_id == exercise_plan_id)
#--------------------------------------------------------

#------------------------ Rutine ------------------------
# DEPRECATED: Use RoutineRepository.get_by_id() instead
def get_rutine_info(db: Session, rutine_id: int):
    return db.query(
        models.Rutine
        ).filter(models.Rutine.rutine_id == rutine_id)
#--------------------------------------------------------

#----------------------- Exercise -----------------------
# DEPRECATED: Use ExerciseRepository.get_by_id() instead
def get_exercise_info(db: Session, exercise_id: int):
    return db.query(
        models.Exercise
    ).filter(models.Exercise.exercise_id == exercise_id)
#--------------------------------------------------------
#*******************************************************************************


#********************************* POST METHODS ********************************
#-------------------- User creation --------------------
# DEPRECATED: Use UserRepository.create() instead
def create_user(db: Session, user: schemas.User_Create):
    db_user = models.User(
        user_name=user.user_name,
        hashed_password=get_password_hash(user.password),
        email=user.email
        )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
#--------------------------------------------------------

#------------------- Exercise creation ---------------------------------------------
# DEPRECATED: Use ExerciseRepository.create() instead
def create_exercise(db: Session, exercise: schemas.Exercise_Create, rutine_id: int):
    db_exercise = models.Exercise(
        **exercise.model_dump(),
        #TODO image,
        rutine_id = rutine_id
        )
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)

    return db_exercise
#-----------------------------------------------------------------------------------

#---------------- Exercise_plan_global creation ----------------
# DEPRECATED: Use ExercisePlanGlobalRepository.create() instead
def create_exercise_plan_global(db: Session, exercise_plan: schemas.Exercise_plan_global_Create, user_id: int):
    db_exercise_plan = models.Exercise_plan_global(
        **exercise_plan.model_dump(),
        user_creator_id=user_id,
        creation_date=datetime.now().date()
    )
    db.add(db_exercise_plan)
    db.commit()
    db.refresh(db_exercise_plan)

    return db_exercise_plan
#--------------------------------------------------------

#------------------------- Rutine_global creation ------------------------
# DEPRECATED: Use RoutineGlobalRepository.create() instead
def create_routine_global(db: Session, rutine_gobal: schemas.Rutine_global_Create):
    db_rutine_global = models.Rutine_global(
        **rutine_gobal.model_dump()
        )
    db.add(db_rutine_global)
    db.commit()
    db.refresh(db_rutine_global)

    return db_rutine_global
#-------------------------------------------------------------------------

#----------------------------- Exercise_global creation ----------------------------
# DEPRECATED: Use ExerciseGlobalRepository.create() instead
def create_exercise_global(db: Session, exercise_global: schemas.Exercise_Create):
    db_exercise = models.Exercise_global(
        **exercise_global.model_dump(),
        )
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)

    return db_exercise
#-----------------------------------------------------------------------------------


# DEPRECATED: Use TrackerRepository.record_exercise_plan_end() instead
def record_end_exercise_plan(db: Session, user_id: int, exercise_record):
    db_exercise_plan_record = models.User_Tracker(
        user_id = user_id,
        info_type = "exercise_plan_end",
        info_description = exercise_record.exercise_plan_id
    )
    db.add(db_exercise_plan_record)
    db.commit()
    db.refresh(db_exercise_plan_record)

    return db_exercise_plan_record


# DEPRECATED: Use TrackerRepository.record_exercise_plan_start() instead
def record_start_exercise_plan(db: Session, user_id: int, exercise_record):
    db_exercise_plan_record = models.User_Tracker(
        user_id = user_id,
        info_type = "exercise_plan_start",
        info_description = exercise_record.exercise_plan_id
    )
    db.add(db_exercise_plan_record)
    db.commit()
    db.refresh(db_exercise_plan_record)

    return db_exercise_plan_record
#*******************************************************************************


#********************************* PUT METHODS *********************************
# DEPRECATED: Use ExercisePlanRepository.assign_to_user() instead
def asign_exercise_plan(db: Session, exercise_plan: schemas.Exercise_plan_Create, user_id: int):

    # Crear nuevo Exercise_plan
    db_exercise_plan = models.Exercise_plan(
        exercise_plan_name=exercise_plan.exercise_plan_name,
        user_owner_id=user_id,
        exercise_plan_type=exercise_plan.exercise_plan_type,
        creation_date=datetime.now().date(),
        difficult_level=exercise_plan.difficult_level,
        routine_group_order=exercise_plan.routine_group_order
        )
    db.add(db_exercise_plan)
    db.flush()
    
    # Copiar las rutinas del Exercise_plan_global al nuevo Exercise_plan
    for rutine_global in exercise_plan.rutines:
        db_rutine = models.Rutine(
            rutine_name=rutine_global.rutine_name,
            rutine_type=rutine_global.rutine_type,
            rutine_group=rutine_global.rutine_group,
            rutine_category=rutine_global.rutine_category,
            exercise_plan_id=db_exercise_plan.exercise_plan_id,
            rounds=rutine_global.rounds,
            rst_btw_exercises=rutine_global.rst_btw_exercises,
            rst_btw_rounds=rutine_global.rst_btw_rounds,
            difficult_level=rutine_global.difficult_level
        )
        db.add(db_rutine)
        db.flush()
        
        # Copiar los ejercicios de la rutina del Exercise_plan_global al nuevo Exercise_plan
        for exercise_global in rutine_global.exercises:
            db_exercise = models.Exercise(
                exercise_name = exercise_global.exercise_name,
                rep = exercise_global.rep,
                exercise_type = exercise_global.exercise_type,
                exercise_group = exercise_global.exercise_group,
                rutine_id = db_rutine.rutine_id,
                image = exercise_global.image
            )
            db.add(db_exercise)
            
    db.commit()
    
    return db_exercise_plan


# DEPRECATED: Use RoutineRepository.update() instead
def update_routine(db, last_routine):
    db.add(last_routine)
    db.commit()
    db.refresh(last_routine)

    return last_routine


# DEPRECATED: Use ExercisePlanRepository.delete_for_user() instead
def delete_exercise_plan_for_user(db: Session, user_id: int):
    """
    Delete exercise plan and all related data for a user.

    OPTIMIZED: Uses subquery to avoid N+1 queries when deleting exercises.
    Instead of iterating over routines and deleting exercises one by one,
    this uses a single bulk delete with IN clause.
    """
    # Get the exercise plan for the user
    exercise_plan = db.query(models.Exercise_plan).filter(
        models.Exercise_plan.user_owner_id == user_id
    ).first()

    if not exercise_plan:
        return False

    # Get all routine IDs for this exercise plan as a subquery
    routine_ids_subquery = select(models.Rutine.rutine_id).where(
        models.Rutine.exercise_plan_id == exercise_plan.exercise_plan_id
    ).scalar_subquery()

    # Delete all exercises associated with these routines in a SINGLE query
    # This avoids the N+1 problem of the previous implementation
    db.query(models.Exercise).filter(
        models.Exercise.rutine_id.in_(routine_ids_subquery)
    ).delete(synchronize_session=False)

    # Delete all routines in a single query
    db.query(models.Rutine).filter(
        models.Rutine.exercise_plan_id == exercise_plan.exercise_plan_id
    ).delete(synchronize_session=False)

    # Delete the exercise plan
    db.query(models.Exercise_plan).filter(
        models.Exercise_plan.user_owner_id == user_id
    ).delete(synchronize_session=False)

    db.commit()

    return True


# DEPRECATED: Use TrackerRepository.record_routine_end_from_dict() instead
def redord_end_rutine(db: Session, user_id: int, exercise_record: dict):

    db_rutine_record = models.User_Tracker(
        **exercise_record,
        user_id=user_id,

    )
    db.add(db_rutine_record)
    db.commit()
    db.refresh(db_rutine_record)

    return db_rutine_record


# =============================================================================
# NEW POLYMORPHIC WORKOUT EVENT FUNCTIONS
# These functions work with the new WorkoutEvent model hierarchy.
# They provide the same functionality but with proper type safety.
# =============================================================================

def record_routine_completed(
    db: Session,
    user_id: int,
    routine_group: str,
    exercise_increments: dict | None = None,
    push_increment: int = 0,
    pull_increment: int = 0,
    isometric_increment: int = 0,
    push_time_increment: int = 0,
    pull_time_increment: int = 0,
    isometric_time_increment: int = 0
) -> models.RoutineCompletedEvent:
    """
    Record a routine completion using the new polymorphic model.

    This is the preferred way to record routine completions going forward.

    Args:
        db: Database session
        user_id: The user's ID
        routine_group: The routine group name
        exercise_increments: Dictionary of exercise-specific increments
        push_increment: Total push exercise increment
        pull_increment: Total pull exercise increment
        isometric_increment: Total isometric exercise increment
        push_time_increment: Total push time increment
        pull_time_increment: Total pull time increment
        isometric_time_increment: Total isometric time increment

    Returns:
        The created RoutineCompletedEvent
    """
    event = models.RoutineCompletedEvent(
        user_id=user_id,
        routine_group=routine_group,
        exercise_increments=exercise_increments,
        push_increment=push_increment,
        pull_increment=pull_increment,
        isometric_increment=isometric_increment,
        push_time_increment=push_time_increment,
        pull_time_increment=pull_time_increment,
        isometric_time_increment=isometric_time_increment
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def record_exercise_plan_started(
    db: Session,
    user_id: int,
    exercise_plan_id: int
) -> models.ExercisePlanStartedEvent:
    """
    Record an exercise plan start using the new polymorphic model.

    Args:
        db: Database session
        user_id: The user's ID
        exercise_plan_id: The exercise plan ID being started

    Returns:
        The created ExercisePlanStartedEvent
    """
    event = models.ExercisePlanStartedEvent(
        user_id=user_id,
        exercise_plan_id=exercise_plan_id
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def record_exercise_plan_completed(
    db: Session,
    user_id: int,
    exercise_plan_id: int
) -> models.ExercisePlanCompletedEvent:
    """
    Record an exercise plan completion using the new polymorphic model.

    Args:
        db: Database session
        user_id: The user's ID
        exercise_plan_id: The exercise plan ID being completed

    Returns:
        The created ExercisePlanCompletedEvent
    """
    event = models.ExercisePlanCompletedEvent(
        user_id=user_id,
        exercise_plan_id=exercise_plan_id
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_last_routine_completion(
    db: Session,
    user_id: int
) -> models.RoutineCompletedEvent | None:
    """
    Get the most recent routine completion for a user.

    Args:
        db: Database session
        user_id: The user's ID

    Returns:
        The most recent RoutineCompletedEvent, or None
    """
    return db.query(models.RoutineCompletedEvent).filter(
        models.RoutineCompletedEvent.user_id == user_id
    ).order_by(
        models.RoutineCompletedEvent.timestamp.desc()
    ).first()


def get_last_exercise_plan_start(
    db: Session,
    user_id: int
) -> models.ExercisePlanStartedEvent | None:
    """
    Get the most recent exercise plan start for a user.

    Args:
        db: Database session
        user_id: The user's ID

    Returns:
        The most recent ExercisePlanStartedEvent, or None
    """
    return db.query(models.ExercisePlanStartedEvent).filter(
        models.ExercisePlanStartedEvent.user_id == user_id
    ).order_by(
        models.ExercisePlanStartedEvent.timestamp.desc()
    ).first()


#---------------------------------------------------------
#*******************************************************************************


# SECURITY: Removed fake_decode_token, fake_decode_token_unsafe, and fake_hash_password
# These test functions were insecure and should not be used in production.
# Removed during security audit 2026-01-09.


# ************************** For logging purposes **************************
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        user = get_user_by_email(db, username)
    
    if not user:
        return False
    
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta, SECRET_KEY: str, ALGORITHM: str| None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encode_jwt
#***************************************************************************