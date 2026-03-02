from pydantic import BaseModel


class Exercise_Base(BaseModel):
    exercise_name: str
    rep: str
    exercise_type: str
    exercise_group: str


class Exercise_Create(Exercise_Base):
    pass


class Exercise(Exercise_Base):
    exercise_id: int
    rutine_id: int

    class Config:
        from_attributes = True


class Exercise_global_Base(BaseModel):
    exercise_name: str
    rep: str
    exercise_type: str
    exercise_group: str


class Exercise_global_Create(Exercise_global_Base):
    rutine_id: int
    image: str | None = None


class Exercise_global(Exercise_global_Base):
    class Config:
        from_attributes = True
