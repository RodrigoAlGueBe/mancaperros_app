from __future__ import annotations
from pydantic import BaseModel
from datetime import date

#----------------- Exercise -------------------
class Exercise_Base(BaseModel):
    exercise_name:str
    #TODO image: Image
    rep:str
    exercise_type:str
    exercise_group:str
    
class Exercise_Create(Exercise_Base):
    pass

class Exercise(Exercise_Base):
    exercise_id:int
    rutine_id: int
    
    class Config:
        orm_mode = True
#---------------------------------------------- 

#------------------ Rutine --------------------
class Rutine_Base(BaseModel):
    rutine_name: str
    rutine_type: str | None = None
    rutine_group: str | None = None
    rutine_category: str | None = None
    
class Rutine_Create(Rutine_Base):
    pass

class Rutine(Rutine_Base):
    rutine_id: int
    exercise_plan_id: int
    
    class Config:
        orm_mode = True
#---------------------------------------------- 

#------------ Exercise_plan -------------------
class Exercise_plan_Base(BaseModel):
    exercise_plan_name: str
    
class Exercise_plan_Create(Exercise_plan_Base):
    exercise_plan_type: str | None = None
    difficult_level: str | None = None
    user_owner_id: int
    creation_date: date | None = None

    rutines: list[Rutine] = []

class Exercise_plan(Exercise_plan_Base):
    user_owner_id: int
    exercise_plan_type: str | None = None
    difficult_level: str | None = None
    
    rutines: list[Rutine] = []
    
    class Config:
        orm_mode = True
#----------------------------------------------

#----------- Exercise_plan_global -------------
class Exercise_plan_global_Base(BaseModel):
    exercise_plan_name: str

class Exercise_plan_global_info(Exercise_plan_global_Base):
    exercise_plan_id: int

class Exercise_plan_global_Response(Exercise_plan_global_Base):
    exercise_plan_type: str | None = None
    difficult_level: str | None = None
    creation_date: date | None = None

    class Config:
        orm_mode = True

class Exercise_plan_global_Create(Exercise_plan_global_Base):
    exercise_plan_type: str | None = None
    difficult_level: str | None = None

class Exercise_plan_global(Exercise_plan_global_Base):
    user_creator_id: int
    exercise_plan_type: str | None = None
    difficult_level: str | None = None
    creation_date: date | None = None
    
    rutines: list[Rutine_global] = []
    
    class Config:
        orm_mode = True
#----------------------------------------------

#-------------- Rutine_global -----------------
class Rutine_global_Base(BaseModel):
    rutine_name: str

class Rutine_global_Create(Rutine_global_Base):
    exercise_plan_id: int
    rutine_type: str | None = None
    rutine_group: str | None = None
    rutine_category: str | None = None
    rounds: int
    rst_btw_exercises: str
    rst_btw_rounds: str
    difficult_level: str | None = None

class Rutine_global(Rutine_global_Base): 
    rounds: int
    rst_btw_exercises: str
    rst_btw_rounds: str
    difficult_level: str | None = None
    
    exercises: list[Exercise_global] = []
    
    class Config:
        orm_mode = True
#----------------------------------------------

#------------- Exercise_global ----------------
class Exercise_global_Base(BaseModel):
    exercise_name: str
    rep: str
    exercise_type: str
    exercise_group: str

class Exercise_global_Create(Exercise_global_Base):
    rutine_id: int
    image: str | None = None


class Exercise_global(Exercise_global_Base):
    pass
    
    class Config:
        orm_mode = True
#----------------------------------------------

#------------------- User ---------------------
class User_Base(BaseModel):
    user_name: str
    email: str

    class Config:
        orm_mode = True

class User_Create(User_Base):
    password: str

class User_Information(User_Base):
    user_id: int

class User(User_Base):
    hashed_password: str
    user_id: int
    
    class Config:
        orm_mode = True
#----------------------------------------------

#------------------- token --------------------
class Token(BaseModel):
    access_token: str
    token_type: str
#----------------------------------------------

Exercise_plan_global.update_forward_refs()
Rutine_global.update_forward_refs()