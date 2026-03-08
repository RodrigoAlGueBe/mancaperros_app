from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Rutine(Base):
    __tablename__ = "rutines"

    rutine_id = Column(Integer, primary_key=True, index=True)
    rutine_name = Column(String(255), unique=False, index=True, default="New rutine name")
    rutine_type = Column(String(255), unique=False, index=True, default="New rutine type")
    rutine_group = Column(String(255), unique=False, index=True, default="New rutine group")
    rutine_category = Column(String(255), unique=False, index=True, default="New rutine category")
    exercise_plan_id = Column(Integer, ForeignKey("exercise_plans.exercise_plan_id"))
    rounds = Column(Integer, unique=False, index=True, default=0)
    rst_btw_exercises = Column(String(255), unique=False, index=True, default="0")
    rst_btw_rounds = Column(String(255), unique=False, index=True, default="0")
    difficult_level = Column(String(255), unique=False, index=True, default="New rutine difficult level")

    owner = relationship("Exercise_plan", back_populates="rutines")
    exercises = relationship("Exercise", back_populates="exercise_owner", cascade="all, delete-orphan")


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
    exercises = relationship("Exercise_global", back_populates="exercise_owner", cascade="all, delete-orphan")
