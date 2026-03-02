from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


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
