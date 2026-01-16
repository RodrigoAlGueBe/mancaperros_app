"""
User Repository - Repository for User entity data access.

This module encapsulates all database operations related to the User entity,
providing a clean interface for user management operations.
"""

from typing import Optional, List, Any, Dict
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt

from .base_repository import BaseRepository

# Import models - adjust path based on your project structure
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
import models


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepository(BaseRepository[models.User, Any, Any]):
    """
    Repository for User entity operations.

    Extends BaseRepository with user-specific queries such as
    authentication, password management, and user lookup by various fields.
    """

    def __init__(self, db: Session):
        """
        Initialize the UserRepository.

        Args:
            db: The database session
        """
        super().__init__(models.User, db)

    def get_by_id(self, user_id: int) -> Optional[models.User]:
        """
        Retrieve a user by their ID.

        Args:
            user_id: The user's primary key

        Returns:
            The User if found, None otherwise
        """
        return self.db.query(models.User).filter(
            models.User.user_id == user_id
        ).first()

    def get_by_username(self, username: str) -> Optional[models.User]:
        """
        Retrieve a user by their username.

        Args:
            username: The user's username

        Returns:
            The User if found, None otherwise
        """
        return self.db.query(models.User).filter(
            models.User.user_name == username
        ).first()

    def get_by_email(self, email: str) -> Optional[models.User]:
        """
        Retrieve a user by their email address.

        Args:
            email: The user's email address

        Returns:
            The User if found, None otherwise
        """
        return self.db.query(models.User).filter(
            models.User.email == email
        ).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[models.User]:
        """
        Retrieve all users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of User entities
        """
        return self.db.query(models.User).offset(skip).limit(limit).all()

    def create(
        self,
        user_name: str,
        email: str,
        password: str,
        user_image: str = "empty"
    ) -> models.User:
        """
        Create a new user with hashed password.

        Args:
            user_name: The user's username
            email: The user's email address
            password: The plain text password (will be hashed)
            user_image: Optional user image path

        Returns:
            The created User entity
        """
        hashed_password = self._get_password_hash(password)
        db_user = models.User(
            user_name=user_name,
            email=email,
            hashed_password=hashed_password,
            user_image=user_image
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def create_from_schema(self, user_schema: Any) -> models.User:
        """
        Create a new user from a Pydantic schema.

        Args:
            user_schema: The user creation schema (with user_name, email, password)

        Returns:
            The created User entity
        """
        return self.create(
            user_name=user_schema.user_name,
            email=user_schema.email,
            password=user_schema.password
        )

    def update(
        self,
        user: models.User,
        user_name: Optional[str] = None,
        email: Optional[str] = None,
        user_image: Optional[str] = None
    ) -> models.User:
        """
        Update user information.

        Args:
            user: The user entity to update
            user_name: New username (optional)
            email: New email (optional)
            user_image: New user image path (optional)

        Returns:
            The updated User entity
        """
        if user_name is not None:
            user.user_name = user_name
        if email is not None:
            user.email = email
        if user_image is not None:
            user.user_image = user_image

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user: models.User, new_password: str) -> models.User:
        """
        Update a user's password.

        Args:
            user: The user entity
            new_password: The new plain text password (will be hashed)

        Returns:
            The updated User entity
        """
        user.hashed_password = self._get_password_hash(new_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: models.User) -> bool:
        """
        Delete a user.

        Args:
            user: The user entity to delete

        Returns:
            True if deletion was successful
        """
        self.db.delete(user)
        self.db.commit()
        return True

    def delete_by_id(self, user_id: int) -> bool:
        """
        Delete a user by their ID.

        Args:
            user_id: The user's primary key

        Returns:
            True if deletion was successful, False if user not found
        """
        deleted_count = self.db.query(models.User).filter(
            models.User.user_id == user_id
        ).delete()
        self.db.commit()
        return deleted_count > 0

    def exists_by_email(self, email: str) -> bool:
        """
        Check if a user exists with the given email.

        Args:
            email: The email address to check

        Returns:
            True if a user exists with that email
        """
        return self.db.query(models.User).filter(
            models.User.email == email
        ).first() is not None

    def exists_by_username(self, username: str) -> bool:
        """
        Check if a user exists with the given username.

        Args:
            username: The username to check

        Returns:
            True if a user exists with that username
        """
        return self.db.query(models.User).filter(
            models.User.user_name == username
        ).first() is not None

    # Authentication methods
    def authenticate(self, username_or_email: str, password: str) -> Optional[models.User]:
        """
        Authenticate a user by username/email and password.

        Args:
            username_or_email: The username or email address
            password: The plain text password

        Returns:
            The User if authentication succeeds, None otherwise
        """
        # Try to find user by username first, then by email
        user = self.get_by_username(username_or_email)
        if not user:
            user = self.get_by_email(username_or_email)

        if not user:
            return None

        if not self._verify_password(password, user.hashed_password):
            return None

        return user

    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: timedelta,
        secret_key: str,
        algorithm: str
    ) -> str:
        """
        Create a JWT access token.

        Args:
            data: The data to encode in the token
            expires_delta: Token expiration time
            secret_key: The secret key for signing
            algorithm: The JWT algorithm to use

        Returns:
            The encoded JWT token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
        return encoded_jwt

    # Private helper methods
    @staticmethod
    def _verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.

        Args:
            plain_password: The plain text password
            hashed_password: The hashed password

        Returns:
            True if the passwords match
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def _get_password_hash(password: str) -> str:
        """
        Hash a plain text password.

        Args:
            password: The plain text password

        Returns:
            The hashed password
        """
        return pwd_context.hash(password)
