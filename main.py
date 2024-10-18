from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta

from typing import Annotated, List
from sqlalchemy.orm import Session, joinedload
from jose import JWTError, jwt

import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.post("/users/exercise_plans_global", response_model=schemas.Exercise_plan_global)
async def create_exercise_plan_global(current_user: Annotated[models.User, Depends(get_current_user)], exercise_plan: schemas.Exercise_plan_global_Create, db: Session = Depends(get_db)):
    
    user_from_email = crud.get_user_by_email(db, user_email=current_user.username)
    if not user_from_email:
        raise HTTPException(status_code=400, detail="User not found")

    if db.query(models.Exercise_plan_global).filter(models.Exercise_plan_global.exercise_plan_name == exercise_plan.exercise_plan_name).first():
        raise HTTPException(
            status_code=400,
            detail="Exercise plan already exists"
        )

    return crud.create_exercise_plan_global(db=db, exercise_plan=exercise_plan, user_id=user_from_email.user_id)


@app.post("/users/exercise_plans_global/routines_global", response_model=schemas.Rutine)
def create_routine_for_exercise_plan(current_user: Annotated[models.User, Depends(get_current_user)], routine: schemas.Rutine_global_Create, db: Session = Depends(get_db)):
    
    user_from_email = crud.get_user_by_email(db, user_email=current_user.username)
    if not user_from_email:
        raise HTTPException(status_code=400, detail="User not found")
    
    exercise_plan = db.query(models.Exercise_plan_global).filter(models.Exercise_plan_global.exercise_plan_id == routine.exercise_plan_id).first()
    if not exercise_plan:
        raise HTTPException(status_code=404, detail="Exercise plan not found")
    
    if db.query(models.Rutine_global).filter(
            models.Rutine_global.rutine_name == routine.rutine_name, 
            models.Rutine_global.exercise_plan_id == routine.exercise_plan_id
        ).first():
        raise HTTPException(status_code=400, detail="Routine name already exists for this exercise plan")
    
    return crud.create_routine_global(db=db, routine=routine, owner=routine.exercise_plan_id)


@app.post("/users/exercise_plans_global/routines_global/exercises_global", response_model=schemas.Exercise_global)
def create_routine_for_exercise_plan(current_user: Annotated[models.User, Depends(get_current_user)], exercise: schemas.Exercise_global_Create, db: Session = Depends(get_db)):
    
    user_from_email = crud.get_user_by_email(db, user_email=current_user.username)
    if not user_from_email:
        raise HTTPException(status_code=400, detail="User not found")
    
    routine = db.query(models.Rutine_global).filter(models.Rutine_global.rutine_id == exercise.rutine_id).first()
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    
    exercise_plan = db.query(models.Exercise_plan_global).filter(models.Exercise_plan_global.exercise_plan_id == routine.exercise_plan_id).first()
    if not exercise_plan:
        raise HTTPException(status_code=404, detail="Exercise plan not found")
    

    if db.query(models.Exsercise_global).filter(
            models.Exercise_plan_global.exercise_plan_id == exercise_plan.exercise_plan_id, 
            models.Rutine_global.rutine_id == routine.rutine_id, 
            models.Exsercise_global.exercise_name == exercise.exercise_name
        ).first():

        raise HTTPException(status_code=400, detail="Exercise name already exists for this Routine")
    
    return crud.create_exercise_global(db=db, exercise_global=exercise)
# ******************************************************************************************************************


# ****************************************************** PUT *******************************************************
@app.put("/users/exercise_plans", response_model=schemas.Exercise_plan)
def asign_exercise_plan_to_user(current_user: Annotated[models.User, Depends(get_current_user)], exercise_plan: schemas.Exercise_plan_global_info, db: Session = Depends(get_db)):
        
    user_from_email = crud.get_user_by_email(db, user_email=current_user.username)
    if not user_from_email:
        raise HTTPException(status_code=400, detail="User not found")
    
    if db.query(models.Exercise_plan).filter(models.Exercise_plan.user_owner_id == user_from_email.user_id).first():
        crud.delete_exercise_plan_for_user(db, user_from_email.user_id)
    
    exercise_plan_global = db.query(models.Exercise_plan_global)\
                             .options(joinedload(models.Exercise_plan_global.rutines))\
                             .filter(models.Exercise_plan_global.exercise_plan_id == exercise_plan.exercise_plan_id).first()
    exercise_plan_global = exercise_plan_global.__dict__
    # Habria que renombrar o cupiar los objetos Rutine_global a Rutine para que el modelo de rutina sea el correcto
    print(exercise_plan_global)
    del exercise_plan_global["exercise_plan_id"]
    del exercise_plan_global["_sa_instance_state"]
    del exercise_plan_global["user_creator_id"]
    
    if not exercise_plan_global:
        raise HTTPException(
            status_code=400,
            detail="Exercise plan not found"
        )
    
    return crud.asign_exercise_plan(db=db, exercise_plan=exercise_plan_global, user_id=user_from_email.user_id)
# ******************************************************************************************************************


# ****************************************************** GET *******************************************************
@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return{"token": token}

async def get_current_active_user(  #Rod 20/08/2023
        current_user: Annotated[models.User, Depends(get_current_user)]
):
    return current_user


@app.get("/users/me", response_model=schemas.User_Information)   #Rod 20/08/2023
async def read_users_me(current_user: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    
    user = crud.get_user_by_email(db=db, user_email=current_user.username)
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


@app.get("/get_user_main_page_info/")
def get_user_main_page(current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):

    user_from_email = crud.get_user_by_email(db, user_email=current_user.username)
    if not user_from_email:
        raise HTTPException(status_code=400, detail="User not found")

    user_exercise_plans = db.query(models.Exercise_plan).filter(models.Exercise_plan.user_owner_id == user_from_email.user_id).first()

    user_data = {
        "user_name": user_from_email.user_name,
        "email": user_from_email.email,
        "user_image": user_from_email.user_image,
        "exercise_plan_name": user_exercise_plans.exercise_plan_name if user_exercise_plans else None,
        "exercise_plan_id": user_exercise_plans.exercise_plan_id if user_exercise_plans else None,
    }

    return user_data


@app.get("/users/get_available_exercise_plans/{exercise_plan_type}", response_model=List[schemas.Exercise_plan_global_Response])
def get_available_exercise_plans(exercise_plan_type, current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):

    exercise_plans = db.query(models.Exercise_plan_global).filter(models.Exercise_plan_global.exercise_plan_type == exercise_plan_type).all()
    if not exercise_plans:
        raise HTTPException(
            status_code=404,
            detail="No exercise plans found"
        )

    return exercise_plans


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

@app.get("/users/get_exercise_plans_muscular_groups/{exercise_plan_name}")
def get_muscular_groups_for_exercise_plans(exercise_plan_name, current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):

    exercise_plan_by_name = db.query(models.Exercise_plan_global).filter(models.Exercise_plan_global.exercise_plan_name == exercise_plan_name).first()
    if not exercise_plan_by_name:
        raise HTTPException(
            status_code=404,
            detail="Exercise plan not found"
        )

    routines = db.query(models.Rutine_global).filter(models.Rutine_global.exercise_plan_id == exercise_plan_by_name.exercise_plan_id).all()
    routine_groups = list(set(routine.rutine_group for routine in routines))

    return routine_groups
# ******************************************************************************************************************

# ***************************************************** LOGIN ******************************************************
@app.post("/token", response_model=schemas.Token)    #Rod 01/10/2023 new token url
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    user_db = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user_db:
        user_db = db.query(models.User).filter(models.User.user_name == form_data.username).first()

    if not user_db:
        raise HTTPException(status_code=400, detail="No user found")

    user = crud.authenticate_user(db, form_data.username, form_data.password)    #Rod 21/10/2023 fake_users_db -> user_db

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires, SECRET_KEY=SECRET_KEY, ALGORITHM=ALGORITHM
    )

    return {"access_token": access_token, "token_type": "bearer"}
# ******************************************************************************************************************