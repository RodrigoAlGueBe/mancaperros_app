"""
User management endpoints.

This module contains endpoints for user operations including:
- User registration
- User profile retrieval
- User listing
- User main page information
"""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_db, get_current_user, DbSession, CurrentUser
import crud
import models
import schemas


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.User_Create, db: DbSession):
    """
    Create a new user.

    Args:
        user: User creation data (username, email, password)
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: 400 if email or username already exists
        HTTPException: 500 if user creation fails
    """
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if db.query(models.User).filter(models.User.user_name == user.user_name).first():
        raise HTTPException(status_code=400, detail="Username already exist")

    created_user = crud.create_user(db=db, user=user)
    if not created_user:
        raise HTTPException(
            status_code=500,
            detail="Error in user creation, user have not been created"
        )

    return {"detail": "User created correctly"}


@router.get("/me", response_model=schemas.User_Information)
async def read_users_me(current_user: CurrentUser, db: DbSession):
    """
    Get current authenticated user's information.

    Args:
        current_user: Current authenticated user from token
        db: Database session

    Returns:
        User_Information: Current user's profile data

    Raises:
        HTTPException: 400 if user not found
    """
    user = crud.get_user_by_email(db=db, user_email=current_user.username)
    if not user:
        raise HTTPException(status_code=400, detail="Email not registered")

    return user


@router.get("/get_user_by_email/{user_email}")
def get_user_by_email(
    user_email: str,
    current_user: CurrentUser,
    db: DbSession
):
    """
    Get user by email address - requires authentication.

    SECURITY: This endpoint now requires authentication and only allows
    users to access their own data (security audit 2026-01-09).

    Args:
        user_email: User's email address
        current_user: Current authenticated user from token
        db: Database session

    Returns:
        User data

    Raises:
        HTTPException: 403 if not authorized to access this user's data
        HTTPException: 400 if email not registered
    """
    # SECURITY: Only allow access to own data
    if current_user.username != user_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's data"
        )

    db_user = crud.get_user_by_email(db, user_email=user_email)

    if not db_user:
        raise HTTPException(status_code=400, detail="Email not registered")

    return db_user


@router.get("/", response_model=None)
def get_all_users(
    current_user: CurrentUser,
    db: DbSession
):
    """
    Get all registered users - REQUIRES ADMIN ROLE.

    SECURITY: This endpoint now requires authentication (security audit 2026-01-09).
    TODO: Implement admin role verification for full security.

    Args:
        current_user: Current authenticated user from token
        db: Database session

    Returns:
        List of all users

    Raises:
        HTTPException: 400 if no users registered
    """
    # TODO: Agregar verificacion de rol de administrador
    # if not is_admin(current_user):
    #     raise HTTPException(status_code=403, detail="Admin access required")

    db_users = crud.get_users(db=db)

    if not db_users:
        raise HTTPException(
            status_code=400,
            detail="Not users in aplication registered yet"
        )

    return db_users


@router.get("/main_page_info")
def get_user_main_page(current_user: CurrentUser, db: DbSession):
    """
    Get user's main page information.

    Returns summary data for displaying on the user's main dashboard,
    including user profile and current exercise plan information.

    Args:
        current_user: Current authenticated user from token
        db: Database session

    Returns:
        Dictionary with user profile and exercise plan summary

    Raises:
        HTTPException: 400 if user not found
    """
    user_from_email = crud.get_user_by_email(db, user_email=current_user.username)
    if not user_from_email:
        raise HTTPException(status_code=400, detail="User not found")

    user_exercise_plans = db.query(models.Exercise_plan).filter(
        models.Exercise_plan.user_owner_id == user_from_email.user_id
    ).first()

    user_data = {
        "user_name": user_from_email.user_name,
        "email": user_from_email.email,
        "user_image": user_from_email.user_image,
        "exercise_plan_name": user_exercise_plans.exercise_plan_name if user_exercise_plans else None,
        "exercise_plan_id": user_exercise_plans.exercise_plan_id if user_exercise_plans else None,
    }

    return user_data


@router.get("/{user_id}/exercise_plans")
async def get_all_exercise_plans_for_user(
    user_id: int,
    current_user: CurrentUser,
    db: DbSession
):
    """
    Get all exercise plans for a specific user.

    Args:
        user_id: User ID to get exercise plans for
        current_user: Current authenticated user from token
        db: Database session

    Returns:
        List of exercise plans for the user

    Raises:
        HTTPException: 401 if not authorized to access this user's data
    """
    user_from_id = crud.get_user_by_id(db, user_id=user_id)
    # current_user.username contains the email (from JWT token "sub" field)
    if user_from_id.email != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorizated to use this user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return db.query(models.Exercise_plan).filter(
        models.Exercise_plan.user_owner_id == user_id
    ).all()
