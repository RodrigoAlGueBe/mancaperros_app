from pydantic import BaseModel


class User_Base(BaseModel):
    user_name: str
    email: str

    class Config:
        from_attributes = True


class User_Create(User_Base):
    password: str


class User_Information(User_Base):
    user_id: int


class User(User_Base):
    hashed_password: str
    user_id: int

    class Config:
        from_attributes = True
