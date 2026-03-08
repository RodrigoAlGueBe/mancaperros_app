from pydantic import BaseModel
from datetime import datetime


class User_tracker_Base(BaseModel):
    user_id: int
    user_tracker_id: int


class User_tracker_exercise_plan(User_tracker_Base):
    info_type: str
    record_datetime: datetime

    class Config:
        from_attributes = True
