from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base
from pydantic import BaseModel


class User(Base):
    __tablename__ = "users"
    
    user_name = Column(String, unique=False, index=True)
    email = Column(String, unique=True, index=True)
    user_id = Column(Integer, primary_key=True, index=True)
    
    exercise_plan = relationship("Exercise_plan", back_populates="exercise_plan_owner")
    
class Exercise_plan(Base):
    __tablename__ = "exercise_plans"
    
    exercise_plan_name = Column(String, unique=False, index=True, default="New exercise plan")
    exercise_plan_id = Column(Integer, primary_key=True, index=True)
    user_owner_id = Column(Integer, ForeignKey("users.user_id"))
    
    rutines = relationship("Rutine", back_populates="owner")
    exercise_plan_owner = relationship("User", back_populates="exercise_plan")
    
class Rutine(Base):
    __tablename__ = "rutines"
    
    rutine_name = Column(String, unique=False, index=True, default="New rutine name")
    rutine_id = Column(Integer, primary_key=True, index=True)
    rutine_type = Column(String, unique=False, index=True, default="New rutine type")
    rutine_group = Column(String, unique=False, index=True, default="New rutine group")
    rutine_category = Column(String, unique=False, index=True, default="New rutine category")
    exercise_plan_id = Column(Integer, ForeignKey("exercise_plans.exercise_plan_id"))
    
    owner = relationship("Exercise_plan", back_populates="rutines")
    exercises = relationship("Exsercise", back_populates="exercise_owner")
    
class Exsercise(Base):
    __tablename__ = "exercises"
    
    exercise_id = Column(Integer, unique=True, index=True, primary_key=True)
    exercise_name = Column(String, unique=False, index=True, default="New exercise name")
    #TODO image = Column...
    rep = Column(String, unique=False, index=True, default="empty")
    exercise_type = Column(String, unique=False, index=True, default="New exercise type")
    exercise_group = Column(String, unique=False, index=True, default="New exercise group")
    rutine_id = Column(Integer, ForeignKey("rutines.rutine_id"))
    
    exercise_owner = relationship("Rutine", back_populates="exercises")


# ************************** For logging purposes **************************
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserInDB(User):
    hashed_password = Column(String, unique=False, index=True)
# **************************************************************************