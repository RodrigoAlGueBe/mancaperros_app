#from msilib import schema
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta

from typing import Annotated
from sqlalchemy.orm import Session
from jose import JWTError, jwt

import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Hashed algorithm and secret key configuration
SECRET_KEY = "f4c961b34a2764b39914debb0b91c22664a44cf16094515f58ef88256291e5fe"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]): #Rod 20/08/2023 
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception
        
        token_data = models.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    return token_data
        

# ****************************************************** POST ******************************************************
# @app.post("/users/", response_model=schemas.User) DEPRECATED
# def create_user(user: schemas.User_Create, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, user_email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     return crud.create_user(db=db, user=user)

@app.post("/users/")
def create_user(user: schemas.User_Create, db: Session = Depends(get_db)):
    """
    Function used for user creation porpouses
    """
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if db.query(models.User).filter(models.User.user_name == user.user_name).first():
        raise HTTPException(status_code=400, detail="Username already exist")
    
    user = crud.create_user(db=db, user=user)
    if not user:
        raise HTTPException(status_code=500, detail="Error in user creation, user have not been created")
    
    return HTTPException(status_code=200, detail="User created correctly")


@app.post("/users/{user_id}/exercise_plans", response_model=schemas.Exercise_plan)
async def create_exercise_plan(user_id: int, exercise_plan: schemas.Exercise_plan_Create, current_user: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):

    user_from_id = crud.get_user_by_id(db, user_id=user_id)
    if user_from_id.user_name != current_user.username:
        raise HTTPException( 
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorizated to use this user",
            headers={"WWW-Authenticate": "Bearer"},
            )
    
    if db.query(models.Exercise_plan).filter(models.Exercise_plan.exercise_plan_name == exercise_plan.exercise_plan_name).first():
        raise HTTPException(
            status_code=400,
            detail="Exercise plan already exists"
        )

    return crud.create_exercise_plan(db=db, exercise_plan=exercise_plan, user_id=user_id)


@app.post("/users/{user_id}/exercise_plans/{exercise_plan_id}/rutines", response_model=schemas.Rutine)
async def create_rutine(user_id: int, exercise_plan_id: int, rutine: schemas.Rutine_Create, current_user: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):

    user_from_id = crud.get_user_by_id(db, user_id=user_id)
    if user_from_id.user_name != current_user.username:
        raise HTTPException( 
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorizated to use this user",
            headers={"WWW-Authenticate": "Bearer"},
            )
    
    if not db.query(models.Exercise_plan).filter(models.Exercise_plan.exercise_plan_id == exercise_plan_id).first():
        raise HTTPException(
            status_code=404,
            detail="Exercise plan not found"
        )
    
    if db.query(models.Rutine).filter(models.Rutine.rutine_name == rutine.rutine_name).first():
        raise HTTPException(
            status_code=400,
            detail="Rutine name already exists"
        )
    
    return crud.create_rutine(db=db, rutine=rutine, owner=exercise_plan_id)


@app.post("/users/{user_id}/exercise_plans/{exercise_plan_id}/rutines/{rutine_id}/exercises", response_model=schemas.Exercise)
def create_exercise(user_id: int, exercise_plan_id: int, rutine_id: int, exercise: schemas.Exercise_Create, current_user: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):

    user_from_id = crud.get_user_by_id(db, user_id=user_id)
    if user_from_id.user_name != current_user.username:
        raise HTTPException( 
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorizated to use this user",
            headers={"WWW-Authenticate": "Bearer"},
            )
    
    if not db.query(models.Exercise_plan).filter(models.Exercise_plan.exercise_plan_id == exercise_plan_id).first():
        raise HTTPException(
            status_code=404,
            detail="Exercise plan not found"
        )
    
    if not db.query(models.Rutine).filter(models.Rutine.rutine_id == rutine_id).first():
        raise HTTPException(
            status_code=404,
            detail="Rutine not found"
        )
    
    if db.query(models.Exsercise).filter(models.Exsercise.exercise_name == exercise.exercise_name).first():
        raise HTTPException(
            status_code=400,
            detail="Exercise name already exists"
        )

    return crud.create_exercise(db=db, exercise=exercise, rutine_id=rutine_id)
# ******************************************************************************************************************

# ****************************************************** GET *******************************************************
@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return{"token": token}

async def get_current_active_user(  #Rod 20/08/2023
        current_user: Annotated[models.User, Depends(get_current_user)]
):
    return current_user


@app.get("/users/me")   #Rod 20/08/2023
async def read_users_me(current_user: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    
    user = crud.get_user_by_username(db=db, username=current_user.username)
    if not user:
        raise HTTPException(status_code=400, detail="Email not registered")
    
    return user


@app.get("/users/get_user_by_email/{user_email}")
def get_user_by_email(user_email, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user_email=user_email)
    
    if not db_user:
        raise HTTPException(status_code=400, detail="Email not registered")
    
    return db_user


@app.get("/get_users/")
def get_all_users(db: Session = Depends(get_db)):
    db_users = crud.get_users(db=db)
    
    if not db_users:
        raise HTTPException(status_code=400, detail="Not users in aplication registered yet")
    
    return db_users


@app.get("/users/{user_id}/exercise_plans")
async def get_all_exercise_plans_for_user(user_id: int, current_user: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    
    user_from_id = crud.get_user_by_id(db, user_id=user_id)
    if user_from_id.user_name != current_user.username:
        raise HTTPException( 
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorizated to use this user",
            headers={"WWW-Authenticate": "Bearer"},
            )
    
    return db.query(models.Exercise_plan).filter(models.Exercise_plan.user_owner_id == user_id).all()


@app.get("/exercise_plans/{exercise_plan_id}/rutines")
async def get_all_rutines_for_exercise_plan(exercise_plan_id: int, db: Session = Depends(get_db)):
    return db.query(models.Rutine).filter(models.Rutine.exercise_plan_id == exercise_plan_id).all()

@app.get("/rutines/{rutine_id}/exercises")
async def get_all_exercises_for_rutine(rutine_id: int, db: Session = Depends(get_db)):
    return db.query(models.Exsercise).filter(models.Exsercise.rutine_id == rutine_id).all()

@app.get("/test/")
def get_test():
    return "Hola mancaperros"
# ******************************************************************************************************************

# ***************************************************** LOGIN ******************************************************
@app.post("/token", response_model=models.Token)    #Rod 01/10/2023 new token url
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    user_db = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user_db:
        user_db = db.query(models.User).filter(models.User.user_name == form_data.username).first()

    if not user_db:
        return HTTPException(status_code=400, detail="No user found")

    user = crud.authenticate_user(db, form_data.username, form_data.password)    #Rod 21/10/2023 fake_users_db -> user_db

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(
        data={"sub": user.user_name}, expires_delta=access_token_expires, SECRET_KEY=SECRET_KEY, ALGORITHM=ALGORITHM
    )

    return {"access_token": access_token, "token_type": "bearer"}

# @app.post("/token") #Rod 20/08/2023
# async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
#     user_dict = fake_users_db.get(form_data.username)
#     if not user_dict:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#     user = models.UserInDB(**user_dict)
#     hashed_password = crud.fake_hash_password(form_data.password)
#     if not hashed_password == user.hashed_password:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
    
#     return {"access_token": user.user_name, "token_type": "bearer"}
# ******************************************************************************************************************