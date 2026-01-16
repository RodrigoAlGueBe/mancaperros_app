"""
User Service Module

This module encapsulates all business logic related to user operations,
separating concerns from the API endpoints and data access layer.
"""

from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from app.infrastructure.database.repositories import (
    UserRepository,
    ExercisePlanRepository,
)


class UserService:
    """
    Service class for handling user-related business logic.

    This service encapsulates all user operations including:
    - User creation with validation
    - User retrieval
    - Authentication and token management
    - Main page data aggregation
    """

    def __init__(self, db: Session):
        """
        Initialize the UserService with a database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.user_repo = UserRepository(db)
        self.exercise_plan_repo = ExercisePlanRepository(db)

    def create_user(self, user_data: schemas.User_Create) -> models.User:
        """
        Create a new user with validation.

        Business rules:
        - Email must be unique across all users
        - Username must be unique across all users

        Args:
            user_data: User creation schema with user details

        Returns:
            The created user model

        Raises:
            HTTPException: If email or username already exists, or if creation fails
        """
        # Validate email uniqueness using repository
        if self.user_repo.exists_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Validate username uniqueness using repository
        if self.user_repo.exists_by_username(user_data.user_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exist"
            )

        # Create user through repository
        user = self.user_repo.create_from_schema(user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error in user creation, user have not been created"
            )

        return user

    def get_user_by_email(self, user_email: str) -> models.User:
        """
        Get a user by their email address.

        Args:
            user_email: The email address to search for

        Returns:
            The user model if found

        Raises:
            HTTPException: If no user is found with the given email
        """
        user = self.user_repo.get_by_email(user_email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not registered"
            )
        return user

    def get_user_by_email_optional(self, user_email: str) -> Optional[models.User]:
        """
        Get a user by their email address without raising an exception.

        Args:
            user_email: The email address to search for

        Returns:
            The user model if found, None otherwise
        """
        return self.user_repo.get_by_email(user_email)

    def get_user_by_id(self, user_id: int) -> Optional[models.User]:
        """
        Get a user by their ID.

        Args:
            user_id: The user ID to search for

        Returns:
            The user model if found, None otherwise
        """
        return self.user_repo.get_by_id(user_id)

    def get_all_users(self, skip: int = 0, limit: int = 100) -> list[models.User]:
        """
        Get all users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of user models

        Raises:
            HTTPException: If no users exist in the application
        """
        users = self.user_repo.get_all(skip=skip, limit=limit)
        if not users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not users in aplication registered yet"
            )
        return users

    def get_current_user_from_token(self, user_email: str) -> models.User:
        """
        Get the current authenticated user by their email from token.

        Args:
            user_email: The email from the JWT token

        Returns:
            The user model

        Raises:
            HTTPException: If user is not found
        """
        user = self.user_repo.get_by_email(user_email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found"
            )
        return user

    def validate_user_authorization(self, user_id: int, current_username: str) -> models.User:
        """
        Validate that the current user is authorized to access the given user_id.

        Args:
            user_id: The user ID being accessed
            current_username: The username from the current authenticated user's token

        Returns:
            The user model if authorized

        Raises:
            HTTPException: If user is not authorized
        """
        user_from_id = self.user_repo.get_by_id(user_id)
        if not user_from_id or user_from_id.user_name != current_username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authorized to use this user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_from_id

    def get_main_page_info(self, user_email: str) -> dict:
        """
        Get aggregated user data for the main page.

        This method combines user profile data with their current exercise plan
        information for display on the main application page.

        Args:
            user_email: The email of the authenticated user

        Returns:
            Dictionary containing user profile and exercise plan data

        Raises:
            HTTPException: If user is not found
        """
        user = self.get_current_user_from_token(user_email)

        # Use repository to get exercise plan
        user_exercise_plans = self.exercise_plan_repo.get_by_user_id(user.user_id)

        return {
            "user_name": user.user_name,
            "email": user.email,
            "user_image": user.user_image,
            "exercise_plan_name": user_exercise_plans.exercise_plan_name if user_exercise_plans else None,
            "exercise_plan_id": user_exercise_plans.exercise_plan_id if user_exercise_plans else None,
        }

    def authenticate_and_create_token(
        self,
        username: str,
        password: str,
        secret_key: str,
        algorithm: str,
        expire_minutes: int
    ) -> dict:
        """
        Authenticate a user and create an access token.

        Args:
            username: Username or email for authentication
            password: User's password
            secret_key: Secret key for JWT encoding
            algorithm: Algorithm for JWT encoding
            expire_minutes: Token expiration time in minutes

        Returns:
            Dictionary containing access_token and token_type

        Raises:
            HTTPException: If user not found or credentials are invalid
        """
        # Check if user exists (by email or username) using repository
        user_db = self.user_repo.get_by_email(username)
        if not user_db:
            user_db = self.user_repo.get_by_username(username)

        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No user found"
            )

        # Authenticate user using repository
        user = self.user_repo.authenticate(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token using repository
        access_token_expires = timedelta(minutes=expire_minutes)
        access_token = self.user_repo.create_access_token(
            data={"sub": user.email},
            expires_delta=access_token_expires,
            secret_key=secret_key,
            algorithm=algorithm
        )

        return {"access_token": access_token, "token_type": "bearer"}


def get_user_service(db: Session) -> UserService:
    """
    Factory function to create a UserService instance.

    This function can be used as a FastAPI dependency.

    Args:
        db: SQLAlchemy database session

    Returns:
        Configured UserService instance
    """
    return UserService(db)
