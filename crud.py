from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from passlib.context import CryptContext
from jose import JWTError, jwt

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
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db, username:str):    #Rod 18/09/2023 documentation get_user -> get_user_by_username
    if username in db:
        user_dict = db[username]
        return models.UserInDB(**user_dict)

#def get_user_by_email(db: Session, user_email: str):    #Rod 20/08/2023 commented
#   return db.query(models.User).filter(models.User.email == user_email).first()    #Rod 20/08/2023 commented
def get_user_by_email(db: Session, user_email: str):    #Rod 20/08/2023 add this function
   if user_email in db:
       user_dict = db[user_email]
       return models.UserInDB(**user_dict)

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
    db_user = models.User(user_name=user.user_name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user
#--------------------------------------------------------

#---------------- Exercise_plan creation ----------------
def create_exercise_plan(db: Session, exercise_plan: schemas.Exercise_plan_Create, user_id: int):
    db_exercise_plan = models.Exercise_plan(exercise_plan_name=exercise_plan.exercise_plan_name, exercise_plan_owner=user_id)
    db.add(db_exercise_plan)
    db.commit()
    db.refresh(db_exercise_plan)
    
    return db_exercise_plan
#--------------------------------------------------------

#-------------------- Rutine creation -------------------
def create_rutine(db: Session, rutine: schemas.Rutine_Create, owner: int):
    db_rutine = models.Rutine(
        rutine_name = rutine.rutine_name,
        rutine_type = rutine.rutine_type,
        rutine_group = rutine.rutine_group,
        rutine_category = rutine.rutine_category,
        owner = owner
        )
    db.add(db_rutine)
    db.commit()
    db.refresh(db_rutine)
    
    return db_rutine
#--------------------------------------------------------

#------------------- Exercise creation ---------------------------------------------
def create_exercise(db: Session, exercise: schemas.Exercise_Create, rutine_id: int):
    db_exercise = models.Exsercise(
        exercise_id = exercise.exercise_id,
        exercise_name = exercise.exercise_name,
        exercise_group = exercise.exercise_group,
        exercise_type = exercise.exercise_type,
        rep = exercise.rep,
        #TODO image,
        exercise_owner = rutine_id
    )
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    
    return db_exercise
#-----------------------------------------------------------------------------------
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

def authenticate_user(fake_db, username: str, password: str):
    user = get_user_by_username(fake_db, username)

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