from sqlalchemy.orm import Session

import models, schemas


#********************************* GET METHODS *********************************
#------------------------- User -------------------------
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, user_email: str):
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

#------------------- Exercise creation ------------------
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
#--------------------------------------------------------
#*******************************************************************************