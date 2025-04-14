from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Date, JSON
from sqlalchemy.orm import relationship, declarative_base

from database import Base
from pydantic import BaseModel

import settings

from datetime import datetime, date, timezone


Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    user_name = Column(String(255), unique=False, index=True)
    hashed_password = Column(String(255), unique=False, index=True)
    email = Column(String(255), unique=True, index=True)
    user_id = Column(Integer, primary_key=True, index=True)
    user_image = Column(String(255), unique=False, index=True, default="empty")
    

    exercise_plan = relationship("Exercise_plan", back_populates="exercise_plan_owner", cascade="all, delete-orphan")
    exercise_plan_global = relationship("Exercise_plan_global", back_populates="exercise_plan_owner")
    user_tracker = relationship("User_Tracker", back_populates="user_tracked")
    
class Exercise_plan(Base):
    __tablename__ = "exercise_plans"
    
    exercise_plan_name = Column(String(255), unique=False, index=True, default="New exercise plan")
    exercise_plan_id = Column(Integer, primary_key=True, index=True)
    user_owner_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    exercise_plan_type = Column(String(255), unique=False, index=True, default="New exercise plan type")
    creation_date = Column(Date, unique=False, index=True, default=date(1970, 1, 1))
    difficult_level = Column(String(255), unique=False, index=True, default="New exercise plan difficult level")
    routine_group_order = Column(JSON, nullable=False, unique=False, default=settings.ROUTINE_GROUP_ORDER_DEFAULT)
    
    rutines = relationship("Rutine", back_populates="owner", cascade="all, delete-orphan")
    exercise_plan_owner = relationship("User", back_populates="exercise_plan")
    
class Rutine(Base):
    __tablename__ = "rutines"
    
    rutine_name = Column(String(255), unique=False, index=True, default="New rutine name")
    rutine_id = Column(Integer, primary_key=True, index=True)
    rutine_type = Column(String(255), unique=False, index=True, default="New rutine type")
    rutine_group = Column(String(255), unique=False, index=True, default="New rutine group")
    rutine_category = Column(String(255), unique=False, index=True, default="New rutine category")
    exercise_plan_id = Column(Integer, ForeignKey("exercise_plans.exercise_plan_id"))
    rounds = Column(Integer, unique=False, index=True, default=0)
    rst_btw_exercises = Column(String(255), unique=False, index=True, default="0")
    rst_btw_rounds = Column(String(255), unique=False, index=True, default="0")
    difficult_level = Column(String(255), unique=False, index=True, default="New rutine difficult level")
    
    owner = relationship("Exercise_plan", back_populates="rutines")
    exercises = relationship("Exsercise", back_populates="exercise_owner", cascade="all, delete-orphan")
    
class Exsercise(Base):
    __tablename__ = "exercises"
    
    exercise_id = Column(Integer, unique=True, index=True, primary_key=True)
    exercise_name = Column(String(255), unique=False, index=True, default="New exercise name")
    rep = Column(String(255), unique=False, index=True, default="empty")
    exercise_type = Column(String(255), unique=False, index=True, default="New exercise type")
    exercise_group = Column(String(255), unique=False, index=True, default="New exercise group")
    rutine_id = Column(Integer, ForeignKey("rutines.rutine_id"))
    image = Column(String(255), unique=False, index=True, default="empty")
    
    exercise_owner = relationship("Rutine", back_populates="exercises")

class Exercise_plan_global(Base):
    __tablename__ = "exercise_plans_global"
    
    exercise_plan_id = Column(Integer, primary_key=True, index=True)
    exercise_plan_name = Column(String(255), nullable=False, unique=False, index=True, default="New exercise plan")
    user_creator_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    exercise_plan_type = Column(String(255), nullable=False, unique=False, index=True, default="New exercise plan type")
    creation_date = Column(Date, nullable=False, unique=False, index=True, default=date(1970, 1, 1))
    difficult_level = Column(String(255), nullable=False, unique=False, index=True, default="New exercise plan difficult level")
    routine_group_order = Column(JSON, nullable=False, unique=False, default=settings.ROUTINE_GROUP_ORDER_DEFAULT)
    
    rutines = relationship("Rutine_global", back_populates="owner", cascade="all, delete-orphan")
    exercise_plan_owner = relationship("User", back_populates="exercise_plan_global")

class Rutine_global(Base):
    __tablename__ = "rutines_global"
    
    rutine_id = Column(Integer, primary_key=True, index=True)
    rutine_name = Column(String(255), nullable=False, unique=False, index=True, default="New rutine name")
    rutine_type = Column(String(255), nullable=False, unique=False, index=True, default="New rutine type")
    rutine_group = Column(String(255), nullable=False, unique=False, index=True, default="New rutine group")
    rutine_category = Column(String(255), nullable=False, unique=False, index=True, default="New rutine category")
    exercise_plan_id = Column(Integer, ForeignKey("exercise_plans_global.exercise_plan_id"), nullable=False)
    rounds = Column(Integer, nullable=False, unique=False, index=True, default=0)
    rst_btw_exercises = Column(String(255), nullable=False, unique=False, index=True, default="0")
    rst_btw_rounds = Column(String(255), nullable=False, unique=False, index=True, default="0")
    difficult_level = Column(String(255), nullable=False, unique=False, index=True, default="New rutine difficult level")
    
    owner = relationship("Exercise_plan_global", back_populates="rutines")
    exercises = relationship("Exsercise_global", back_populates="exercise_owner", cascade="all, delete-orphan")

class Exsercise_global(Base):
    __tablename__ = "exercises_global"
    
    exercise_id = Column(Integer, primary_key=True, index=True)
    exercise_name = Column(String(255), nullable=False, unique=False, index=True, default="New exercise name")
    rep = Column(String(255), nullable=False, unique=False, index=True, default="empty")
    exercise_type = Column(String(255), nullable=False, unique=False, index=True, default="New exercise type")
    exercise_group = Column(String(255), nullable=False, unique=False, index=True, default="New exercise group")
    rutine_id = Column(Integer, ForeignKey("rutines_global.rutine_id"), nullable=False)
    image = Column(String(255), nullable=False, unique=False, index=True, default="empty")

    exercise_owner = relationship("Rutine_global", back_populates="exercises")
    
class User_Tracker(Base):
    __tablename__ = "users_tracker"
    
    user_tracker_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    record_datetime = Column(DateTime, nullable=False, unique=False, index=True, default=datetime.now(timezone.utc).replace(tzinfo=None))
    info_type = Column(String(255), nullable=False, unique=False, index=True, default="Non_specifed")
    info_description = Column(String(255), nullable=True, unique=False, index=True, default="Non_specifed")
    exercise_increments = Column(JSON, nullable=True, unique=False, default=None)
    push_increment = Column(Integer, nullable=False, unique=False, default=0)
    pull_increment = Column(Integer, nullable=False, unique=False, default=0)
    isometric_increment = Column(Integer, nullable=False, unique=False, default=0)
    push_time_increment = Column(Integer, nullable=False, unique=False, default=0)
    pull_time_increment = Column(Integer, nullable=False, unique=False, default=0)
    isometric_time_increment = Column(Integer, nullable=False, unique=False, default=0)
    
    user_tracked = relationship("User", back_populates="user_tracker")
    

# ************************** For logging purposes **************************
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# class UserInDB(User):
#     hashed_password = Column(String(255), unique=False, index=True)
# **************************************************************************