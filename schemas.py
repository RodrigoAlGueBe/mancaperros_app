from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime

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
    model_config = ConfigDict(from_attributes=True)

    exercise_id:int
    rutine_id: int
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
    model_config = ConfigDict(from_attributes=True)

    rutine_id: int
    exercise_plan_id: int
#---------------------------------------------- 

#------------ Exercise_plan -------------------
class Exercise_plan_Base(BaseModel):
    exercise_plan_name: str
    
class Exercise_plan_Create(Exercise_plan_Base):
    exercise_plan_type: str | None = None
    difficult_level: str | None = None
    user_owner_id: int
    creation_date: date | None = None
    routine_group_order: list[str] = []

    rutines: list[Rutine] = []

class Exercise_plan(Exercise_plan_Base):
    user_owner_id: int
    exercise_plan_type: str | None = None
    difficult_level: str | None = None
    routine_group_order: list[str] = []

    rutines: list[Rutine] = []

    model_config = ConfigDict(from_attributes=True)
#----------------------------------------------

#----------- Exercise_plan_global -------------
class Exercise_plan_global_Base(BaseModel):
    exercise_plan_name: str

class Exercise_plan_global_info(Exercise_plan_global_Base):
    exercise_plan_id: int

class Exercise_plan_global_Response(Exercise_plan_global_Base):
    model_config = ConfigDict(from_attributes=True)

    exercise_plan_id: int
    exercise_plan_type: str | None = None
    difficult_level: str | None = None
    creation_date: date | None = None
    user_creator_id: int

class Exercise_plan_global_Create(Exercise_plan_global_Base):
    exercise_plan_type: str | None = None
    difficult_level: str | None = None
    routine_group_order: list[str] = []

class Exercise_plan_global(Exercise_plan_global_Base):
    user_creator_id: int
    exercise_plan_type: str | None = None
    difficult_level: str | None = None
    creation_date: date | None = None
    routine_group_order: list[str] = []

    rutines: list[Rutine_global] = []

    model_config = ConfigDict(from_attributes=True)
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
    model_config = ConfigDict(from_attributes=True)

    rounds: int
    rst_btw_exercises: str
    rst_btw_rounds: str
    difficult_level: str | None = None

    exercises: list[Exercise_global] = []
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
    model_config = ConfigDict(from_attributes=True)
#----------------------------------------------

#------------------- User ---------------------
class User_Base(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_name: str
    email: str

class User_Create(User_Base):
    password: str

class User_Information(User_Base):
    user_id: int

class User(User_Base):
    hashed_password: str
    user_id: int
#----------------------------------------------

#--------------- User_tracker -----------------
# LEGACY: These schemas are for backward compatibility with the old User_Tracker model.
# For new code, use the WorkoutEvent schemas below.
class User_tracker_Base(BaseModel):
    user_id: int
    user_tracker_id: int

class User_tracker_exercise_plan(User_tracker_Base):
    model_config = ConfigDict(from_attributes=True)

    info_type: str
    record_datetime: datetime
#----------------------------------------------

#============== WORKOUT EVENTS (HIGH-08) ==============
# New polymorphic event schemas replacing User_Tracker
# These schemas correspond to the new WorkoutEvent model hierarchy.

class WorkoutEventBase(BaseModel):
    """Base schema for all workout events."""
    user_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkoutEventResponse(WorkoutEventBase):
    """Response schema for generic workout events."""
    event_id: int
    event_type: str


class RoutineCompletedEventCreate(BaseModel):
    """Schema for creating a routine completion event."""
    routine_group: str
    exercise_increments: dict[str, int] | None = None
    push_increment: int = 0
    pull_increment: int = 0
    isometric_increment: int = 0
    push_time_increment: int = 0
    pull_time_increment: int = 0
    isometric_time_increment: int = 0


class RoutineCompletedEventResponse(WorkoutEventBase):
    """Response schema for routine completion events."""
    event_id: int
    event_type: str = "routine_completed"
    routine_group: str | None = None
    exercise_increments: dict[str, int] | None = None
    push_increment: int | None = 0
    pull_increment: int | None = 0
    isometric_increment: int | None = 0
    push_time_increment: int | None = 0
    pull_time_increment: int | None = 0
    isometric_time_increment: int | None = 0


class ExercisePlanStartedEventCreate(BaseModel):
    """Schema for creating an exercise plan start event."""
    exercise_plan_id: int


class ExercisePlanStartedEventResponse(WorkoutEventBase):
    """Response schema for exercise plan start events."""
    event_id: int
    event_type: str = "exercise_plan_started"
    exercise_plan_id: int | None = None


class ExercisePlanCompletedEventCreate(BaseModel):
    """Schema for creating an exercise plan completion event."""
    exercise_plan_id: int


class ExercisePlanCompletedEventResponse(WorkoutEventBase):
    """Response schema for exercise plan completion events."""
    event_id: int
    event_type: str = "exercise_plan_completed"
    exercise_plan_id: int | None = None


class UserWorkoutStatistics(BaseModel):
    """Schema for user workout statistics summary."""
    total_routines_completed: int
    total_exercise_plans_completed: int
    total_push_increment: int
    total_pull_increment: int
    total_isometric_increment: int
    total_push_time_increment: int
    total_pull_time_increment: int
    total_isometric_time_increment: int

    model_config = ConfigDict(from_attributes=True)


class NextRoutineResponse(BaseModel):
    """Response schema for next routine recommendation."""
    routine: str
    routine_id: int
#======================================================

#------------------- token --------------------
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
#----------------------------------------------

Exercise_plan_global.model_rebuild()
Rutine_global.model_rebuild()