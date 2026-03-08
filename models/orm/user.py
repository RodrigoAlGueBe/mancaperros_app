from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(255), unique=False, index=True)
    hashed_password = Column(String(255), unique=False, index=True)
    email = Column(String(255), unique=True, index=True)
    user_image = Column(String(255), unique=False, index=True, default="empty")

    exercise_plan = relationship("Exercise_plan", back_populates="exercise_plan_owner", cascade="all, delete-orphan")
    exercise_plan_global = relationship("Exercise_plan_global", back_populates="exercise_plan_owner")
    user_tracker = relationship("User_Tracker", back_populates="user_tracked")
