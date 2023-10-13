#from msilib import schema
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta

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

fake_users_db = {   #Rod 20/08/2023 added fake user for testing propouses 
    "johndoe": {
        "user_name": "johndoe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    },
}

# @app.post("/token") #Rod 20/08/2023 DEPRECATED
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

# ****************************************************** GET *******************************************************
@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return{"token": token}

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
    
    user = crud.get_user_by_username(fake_users_db, username=token_data.username)

    if user is None:
        raise credentials_exception
    
    return user

    # DEPRECATED WAY
    # user = crud.fake_decode_token_unsafe(token)
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid authentication credentials",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    # return user

async def get_current_active_user(  #Rod 20/08/2023
        current_user: Annotated[models.User, Depends(get_current_user)]
):
    return current_user

@app.get("/users/me")   #Rod 20/08/2023
async def read_users_me(current_user: Annotated[str, Depends(get_current_user)]):
    print("***********&&&&&&&&&&&&&&")
    return current_user

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
        raise HTTPException(status_code=400, detail="Not Users in aplication registered yet")
    
    return db_users

@app.get("/test/")
def get_test():
    return "Hola mancaperros"
# ******************************************************************************************************************

# ***************************************************** LOGIN ******************************************************
@app.post("/token", response_model=models.Token)    #Rod 01/10/2023 new token url
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = crud.authenticate_user(fake_users_db, form_data.username, form_data.password)

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