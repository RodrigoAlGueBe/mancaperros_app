from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from passlib.context import CryptContext
from jose import jwt

import models, schemas


fake_users_db = {   #Rod 20/08/2023 added fake user for testing propouses 
    "johndoe": {
        "user_name": "johndoe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    },
}


#********************************* GET METHODS *********************************
#------------------------- User -------------------------
def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_user_by_username(db: Session, username:str):    #Rod 18/09/2023 documentation get_user -> get_user_by_username
    return db.query(models.User).filter(models.User.user_name == username).first()

#def get_user_by_email(db: Session, user_email: str):    #Rod 20/08/2023 commented
#   return db.query(models.User).filter(models.User.email == user_email).first()    #Rod 20/08/2023 commented
def get_user_by_email(db: Session, user_email: str):    #Rod 20/08/2023 add this function
   return db.query(models.User).filter(models.User.email == user_email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()
#--------------------------------------------------------

#-------------------- Exercise_plan ---------------------
def get_exercise_plan_info(db: Session, exercise_plan_id: int):
    return db.query(
        models.Exercise_plan
        ).filter(models.Exercise_plan.exercise_plan_id == exercise_plan_id)
#--------------------------------------------------------

#------------------------ Rutine ------------------------
def get_rutine_info(db: Session, rutine_id: int):
    return db.query(
        models.Rutine
        ).filter(models.Rutine.rutine_id == rutine_id)
#--------------------------------------------------------

#----------------------- Exercise -----------------------
def get_exercise_info(db: Session, exercise_id: int):
    return db.query(
        models.Exsercise
    ).filter(models.Exsercise.exercise_id == exercise_id)
#--------------------------------------------------------
#*******************************************************************************


#********************************* POST METHODS ********************************
#-------------------- User creation --------------------
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
def create_exercise(db: Session, exercise: schemas.Exercise_Create, rutine_id: int):
    db_exercise = models.Exsercise(
        **exercise.dict(),
        #TODO image,
        rutine_id = rutine_id
        )
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    
    return db_exercise
#-----------------------------------------------------------------------------------

#---------------- Exercise_plan_global creation ----------------
def create_exercise_plan_global(db: Session, exercise_plan: schemas.Exercise_plan_global_Create, user_id: int):
    db_exercise_plan = models.Exercise_plan_global(
        **exercise_plan.dict(), 
        user_creator_id=user_id, 
        creation_date=datetime.now().date()
    )
    db.add(db_exercise_plan)
    db.commit()
    db.refresh(db_exercise_plan)
    
    return db_exercise_plan
#--------------------------------------------------------

#------------------------- Rutine_global creation ------------------------
def create_routine_global(db: Session, exercise_gobal: schemas.Rutine_global_Create, owner: int):
    db_rutine_global = models.Rutine_global(
        **exercise_gobal.dict()
        )
    db.add(db_rutine_global)
    db.commit()
    db.refresh(db_rutine_global)
    
    return db_rutine_global
#-------------------------------------------------------------------------

#----------------------------- Exercise_global creation ----------------------------
def create_exercise_global(db: Session, exercise_global: schemas.Exercise_Create):
    db_exercise = models.Exsercise_global(
        **exercise_global.dict(),
        )
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    
    return db_exercise
#-----------------------------------------------------------------------------------


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
def asign_exercise_plan(db: Session, exercise_plan: schemas.Exercise_plan_Create, user_id: int):
    
    # Crear nuevo Exercise_plan
    db_exercise_plan = models.Exercise_plan(
        exercise_plan_name=exercise_plan.exercise_plan_name,
        user_owner_id=user_id,
        exercise_plan_type=exercise_plan.exercise_plan_type,
        creation_date=datetime.now().date(),
        difficult_level=exercise_plan.difficult_level
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
            db_exercise = models.Exsercise(
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


def update_routine(db, last_routine):
    db.add(last_routine)
    db.commit()
    db.refresh(last_routine)
    
    return last_routine


def delete_exercise_plan_for_user(db: Session, user_id: int):
    # Get all exercise plans for the user
    exercise_plan = db.query(models.Exercise_plan).filter(
        models.Exercise_plan.user_owner_id == user_id
    ).first()

    #if db.query(models.Rutine).filter(models.Rutine.exercise_plan_id == exercise_plan.exercise_plan_id).all():
    # Get all routines associated with the exercise plan
    routines = db.query(models.Rutine).filter(
        models.Rutine.exercise_plan_id == exercise_plan.exercise_plan_id
    ).all()
    
    for routine in routines:
        # Delete all exercises associated with the routine
        db.query(models.Exsercise).filter(
            models.Exsercise.rutine_id == routine.rutine_id
        ).delete()
    
    # Delete the routine
    db.query(models.Rutine).filter(
        models.Rutine.exercise_plan_id == exercise_plan.exercise_plan_id
    ).delete()
    
    # Delete the exercise plan
    db.query(models.Exercise_plan).filter(
        models.Exercise_plan.user_owner_id == user_id
    ).delete()
    
    db.commit()
    
    return True


def redord_end_rutine(db: Session, user_id: int, exercise_record: dict):

    db_rutine_record = models.User_Tracker(
        **exercise_record,
        user_id=user_id,

    )
    db.add(db_rutine_record)
    db.commit()
    db.refresh(db_rutine_record)

    return db_rutine_record
    
#---------------------------------------------------------
#*******************************************************************************


# AUXILIAR
def fake_decode_token(token):
    return schemas.User(
        user_name=token + "fakedecoded", email="john@example.com", user_id=9999
    )

def fake_decode_token_unsafe(token):    #Rod 18/09/2023 documentation fake_decode_token -> fake_decode_token_unsafe
    user = get_user_by_username(fake_users_db, token)
    return user

def fake_hash_password(password: str):
    return "fakehashed" + password


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
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encode_jwt
#***************************************************************************