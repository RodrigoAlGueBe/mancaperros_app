from pydantic import BaseModel

#----------------- Exercise -------------------
class Exercise_Base(BaseModel):
    exercise_id:int
    exercise_name:str
    #TODO image: Image
    rep:str
    exercise_type:str
    exercise_group:str
    
class Exercise_Create(Exercise_Base):
    pass

class Exercise(Exercise_Base):
    exercise_owner: int
    
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
    owner: int
    
    class Config:
        orm_mode = True
#---------------------------------------------- 

#------------ Exercise_plan -------------------
class Exercise_plan_Base(BaseModel):
    exercise_plan_name: str
    
class Exercise_plan_Create(Exercise_plan_Base):
    pass

class Exercise_plan(Exercise_plan_Base):
    exercise_plan_id: int
    exercise_plan_owner: int
    rutines: list[Rutine] = []
    
    class Config:
        orm_mode = True
#----------------------------------------------

#------------------- User ---------------------
class User_Base(BaseModel):
    user_name: str
    email: str

class User_Create(User_Base):
    pass

class User(User_Base):
    user_id: int
    
    class Config:
        orm_mode = True
#----------------------------------------------