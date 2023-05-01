from msilib import schema
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

# ****************************************************** POST ******************************************************
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.User_Create, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user_email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return crud.create_user(db=db, user=user)

@app.post("/users/{user_id}/exercise_plans", response_model=schemas.Exercise_plan)
def create_exercise_plan(user_id: int, exercise_plan: schemas.Exercise_plan_Create, db: Session = Depends(get_db)):
    return crud.create_exercise_plan(db=db, exercise_plan=exercise_plan, user_id=user_id)

@app.post("/exercise_plans/{exercise_plan_id}/rutines", response_model=schemas.Rutine)
def create_rutine(exercise_plan_id: int, rutine: schemas.Rutine_Create, db: Session = Depends(get_db)):
    return crud.create_rutine(db=db, rutine=rutine, owner=exercise_plan_id)

@app.post("/rutines/{rutine_id}/exercises", response_model=schemas.Exercise)
def create_exercise(rutine_id: int, exercise: schemas.Exercise_Create, db: Session = Depends(get_db)):
    return crud.create_exercise(db=db, exercise=exercise, rutine_id=rutine_id)
# ******************************************************************************************************************

# ****************************************************** GET *******************************************************
@app.get("/users/get_user_by_email/{user_email}")
def get_user_by_email(user_email, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user_email=user_email)
    
    if not db_user:
        raise HTTPException(status_code=400, detail="Email not registered")
    
    return db_user
    
# ******************************************************************************************************************