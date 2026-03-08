from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from database import Base


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
