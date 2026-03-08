from sqlalchemy import Column, ForeignKey, Index, Integer, String, Date, JSON
from sqlalchemy.orm import relationship
from datetime import date

from database import Base
import settings


class Exercise_plan(Base):
    __tablename__ = "exercise_plans"
    __table_args__ = (
        Index("ix_exercise_plans_user_plan", "user_owner_id", "exercise_plan_id"),
    )

    exercise_plan_id = Column(Integer, primary_key=True, index=True)
    exercise_plan_name = Column(String(255), unique=False, index=True, default="New exercise plan")
    user_owner_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    exercise_plan_type = Column(String(255), unique=False, index=True, default="New exercise plan type")
    creation_date = Column(Date, unique=False, index=True, default=date(1970, 1, 1))
    difficult_level = Column(String(255), unique=False, index=True, default="New exercise plan difficult level")
    routine_group_order = Column(JSON, nullable=False, unique=False, default=settings.ROUTINE_GROUP_ORDER_DEFAULT)

    rutines = relationship("Rutine", back_populates="owner", cascade="all, delete-orphan")
    exercise_plan_owner = relationship("User", back_populates="exercise_plan")


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
