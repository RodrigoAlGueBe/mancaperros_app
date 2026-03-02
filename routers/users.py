from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated

import models
import schemas
from core.dependencies import get_db, get_current_user
from services.user_service import UserService

router = APIRouter(
    tags=["Users"],
)


@router.post("/users/")
def create_user(user: schemas.User_Create, db: Session = Depends(get_db)):
    """
    Function used for user creation porpouses
    """
    try:
        UserService.create_user(db=db, user=user)
        return HTTPException(status_code=200, detail="User created correctly")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/me", response_model=schemas.User_Information)
async def read_users_me(
    current_user: Annotated[str, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    try:
        return UserService.get_current_user_info(db=db, email=current_user.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users/get_user_by_email/{user_email}", response_model=schemas.User_Information)
def get_user_by_email(
    user_email: str,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    try:
        return UserService.get_user_by_email(db=db, email=user_email)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/get_users/")
def get_all_users(db: Session = Depends(get_db)):
    try:
        return UserService.get_all_users(db=db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/get_user_main_page_info/")
def get_user_main_page(
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    try:
        return UserService.get_main_page_info(db=db, email=current_user.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
