from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta, datetime, timezone

from typing import Annotated, List
from sqlalchemy.orm import Session, joinedload
from jose import JWTError, jwt
import json
import logging

import crud, models, schemas
from database import SessionLocal, engine

from utils.functions import f_unit_type_finder, f_reps_to_seconds

models.Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3100",
    "http://localhost:5173",
    "https://blue-water-043a88803.6.azurestaticapps.net"
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
ACCESS_TOKEN_EXPIRE_MINUTES = 180

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


@app.post("/users/end_routine")
async def end_routine(current_user: Annotated[models.User, Depends(get_current_user)], exercises_summary:dict, db: Session = Depends(get_db)):
    
    # Obtenemos el usuario
    user_from_email = crud.get_user_by_email(db, user_email=current_user.username)
    if not user_from_email:
        raise HTTPException(status_code=400, detail="User not found")

    # Obtenemos el ultimo registro de plan de ejericios empezado
    last_exercise_plan = db.query(models.Exercise_plan).filter(
        models.Exercise_plan.user_owner_id == user_from_email.user_id
    ).first()

    # Obtenemos la rutina actual
    last_routine = db.query(models.Rutine).filter(
        models.Rutine.exercise_plan_id == last_exercise_plan.exercise_plan_id,
        models.Rutine.rutine_group == exercises_summary["routine_group"]
    ).first()

    # Actualizamos los ejercicios de la rutina
    exercises_receibed = exercises_summary["exercises"]
    exercise_quantity = len(exercises_receibed)

    ## Comprobamos que el número de ejercicios por rutina coincida
    if exercise_quantity != len(last_routine.exercises):
        raise HTTPException(status_code=500, detail="Received routine does not match with started routine")

    exercise_order_name = "exercise_"
    exercise_secuence = "start"
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
        new_reps = exercises_receibed[exercise_order_name + str(exercise_secuence)]["reps"]
        exercise_record["exercise_increments"][exercise_db.exercise_name] = int(exercise_db.rep) - int(new_reps)
        exercise_db.rep = new_reps

        exercise_type = exercise_db.exercise_type.split('-')

        # Actualizamos los incrementos
        if exercise_type[0] == "push":
            exercise_record["push_increment"] += int(exercise_db.rep) - int(new_reps)
        elif exercise_type[0] == "pull":
            exercise_record["pull_increment"] += int(exercise_db.rep) - int(new_reps)
        else:
            exercise_record["isometric_increment"] += int(f_reps_to_seconds(exercise_db.rep)) - int(f_reps_to_seconds(new_reps))

        # Actualizamos el número del ejercicio
        if exercise_secuence == "start":
            exercise_secuence = 2
        elif exercise_secuence == "end":
            break
        elif int(exercise_secuence) < exercise_quantity - 1:
            exercise_secuence += 1
        else:
            exercise_secuence = "end"
    
    # Actualizamos la rutina
    crud.update_routine(db, last_routine)

    # Creamos el registro de rutina terminada
    crud.redord_end_rutine(db, user_from_email.user_id, exercise_record)

    return {"detail": "Routine ended correctly"}    
# ******************************************************************************************************************


# ****************************************************** PUT *******************************************************
@app.put("/users/exercise_plans", response_model=schemas.User_tracker_exercise_plan)
def asign_exercise_plan_to_user(current_user: Annotated[models.User, Depends(get_current_user)], exercise_plan: schemas.Exercise_plan_global_info, db: Session = Depends(get_db)):

    user_from_email = crud.get_user_by_email(db, user_email=current_user.username)
    if not user_from_email:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Get and clean exercise plan
    exercise_plan_global = db.query(models.Exercise_plan_global)\
                             .options(joinedload(models.Exercise_plan_global.rutines))\
                             .filter(models.Exercise_plan_global.exercise_plan_id == exercise_plan.exercise_plan_id).first()
    
    if db.query(models.Exercise_plan).filter(models.Exercise_plan.user_owner_id == user_from_email.user_id).first():
        crud.delete_exercise_plan_for_user(db, user_from_email.user_id)
        crud.record_end_exercise_plan(db, user_from_email.user_id, exercise_plan_global)
   
    if not exercise_plan_global:
        raise HTTPException(
            status_code=400,
            detail="Exercise plan not found"
        )
    
    # Asigar plan de ejercicios al usuario
    crud.asign_exercise_plan(db=db, exercise_plan=exercise_plan_global, user_id=user_from_email.user_id)

    # Crear record de inicio de plan de ejercicios
    response = crud.record_start_exercise_plan(db, user_from_email.user_id, exercise_plan_global)
    
    return {
        "user_id": response.user_id,
        "user_tracker_id": response.user_tracker_id,
        "info_type": response.info_type,
        "record_datetime": response.record_datetime
    }
    
    # return crud.asign_exercise_plan(db=db, exercise_plan=exercise_plan_global, user_id=user_from_email.user_id) DEPRECATED
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


@app.get("/rutines/get_asigned_routines")
async def get_asigned_routines(current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):

    user_from_email = crud.get_user_by_email(db, user_email=current_user.username)
    if not user_from_email:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Obtenemos el plan de ejercicios actual
    asigned_exercise_plan = db.query(models.Exercise_plan).filter(models.Exercise_plan.user_owner_id == user_from_email.user_id).first()
    
    return db.query(models.Rutine).filter(models.Rutine.exercise_plan_id == asigned_exercise_plan.exercise_plan_id).all()


@app.get("/rutines/{rutine_id}/exercises")  # TODO adaptar a lo nuevo
async def get_all_exercises_for_rutine(rutine_id: int, current_user: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    
    if not db.query(models.Rutine).filter(models.Rutine.rutine_id == rutine_id).first():
        raise HTTPException(
            status_code=404,
            detail="Rutine not found"
        )
    
    routine = db.query(models.Rutine).filter(models.Rutine.rutine_id == rutine_id).first()
    exercises = db.query(models.Exsercise).filter(models.Exsercise.rutine_id == rutine_id).all()

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


@app.get("/test/")
def get_test():
    return "Hola mancaperros"

@app.get("/users/get_exercise_plans_muscular_groups/{exercise_plan_name}")
def get_muscular_groups_for_exercise_plans(exercise_plan_name, current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    # TODO, refactorizar esta función para eliminar exercise_plan_name, y también en el front

    user_by_email = crud.get_user_by_email(db, user_email=current_user.username)
    if not user_by_email:
        raise HTTPException(status_code=400, detail="User not found")
    
    exercise_plan = db.query(models.Exercise_plan).filter(models.Exercise_plan.user_owner_id == user_by_email.user_id).first()

    routines = db.query(models.Rutine).filter(models.Rutine.exercise_plan_id == exercise_plan.exercise_plan_id).all()
    routine_groups = list({"rutine_group": routine.rutine_group, "rutine_id": routine.rutine_id} for routine in routines) #TODO devolver lista de grupos con id de rutinas, diccionario de listas

    return routine_groups

@app.get("/users/get_next_routine")
def get_next_routine(current_user: Annotated[models.User, Depends(get_current_user)], db: Session = Depends(get_db)):
    
    user_by_email = crud.get_user_by_email(db, user_email=current_user.username)
    if not user_by_email:
        raise HTTPException(status_code=400, detail="User not found")
    
    active_exercise_plan = db.query(models.Exercise_plan)\
                             .filter(models.Exercise_plan.user_owner_id == user_by_email.user_id).first()
    if not active_exercise_plan:
        raise HTTPException(status_code=404, detail="No active exercise plan found")
    print("********************" + str(type(active_exercise_plan.routine_group_order)))
    
    try:
        routine_order = json.loads(active_exercise_plan.routine_group_order)
    except (ValueError, TypeError):
        routine_order = active_exercise_plan.routine_group_order

    last_routine = db.query(models.User_Tracker).filter(
                                    models.User_Tracker.user_id == user_by_email.user_id,
                                    models.User_Tracker.info_type == "rutine_end"
                                ).order_by(models.User_Tracker.record_datetime.desc()).first()
    
    if db.query(models.User_Tracker).filter(
        models.User_Tracker.user_id == user_by_email.user_id,
        models.User_Tracker.info_type == "exercise_plan_start"
        ).order_by(models.User_Tracker.record_datetime.desc()).first().record_datetime > last_routine.record_datetime:

        next_routine = routine_order.pop(0)
    

    else:
        last_routine = last_routine.info_description
        n = 0
        for muscular_group in routine_order:
            if (muscular_group == last_routine) and (n + 1 < len(routine_order)):
                next_routine = routine_order[n + 1]
                break
            elif (muscular_group == last_routine) and (n + 1 >= len(routine_order)):
                next_routine = routine_order[0]
                break
            else:
                n += 1

    # Obtención del id de la rutina
    next_routine_id = db.query(models.Rutine).filter(
        models.Rutine.exercise_plan_id == active_exercise_plan.exercise_plan_id,
        models.Rutine.rutine_group == next_routine
    ).first().rutine_id

    next_routine_dict = {
        'routine': next_routine,
        'routine_id': next_routine_id
    }

    return next_routine_dict
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