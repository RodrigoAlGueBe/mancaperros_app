"""
User Repository implementation.

This module provides data access operations for User entities,
encapsulating all user-related database queries.
"""

from typing import Sequence
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt

import models
import schemas
from infrastructure.database.repositories.base_repository import BaseRepository


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepository(BaseRepository[models.User, schemas.User_Create, schemas.User_Base]):
    """
    Repository for User entity operations.

    Provides methods for user CRUD operations, authentication,
    and user-specific queries.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize the User repository.

        Args:
            db: The database session
        """
        super().__init__(models.User, db)

    def get_by_id(self, user_id: int) -> models.User | None:
        """
        Retrieve a user by their ID.

        Args:
            user_id: The user's primary key

        Returns:
            The User instance if found, None otherwise
        """
        return self.db.query(models.User).filter(
            models.User.user_id == user_id
        ).first()

    def get_by_username(self, username: str) -> models.User | None:
        """
        Retrieve a user by their username.

        Args:
            username: The user's username

        Returns:
            The User instance if found, None otherwise
        """
        return self.db.query(models.User).filter(
            models.User.user_name == username
        ).first()

    def get_by_email(self, email: str) -> models.User | None:
        """
        Retrieve a user by their email address.

        Args:
            email: The user's email address

        Returns:
            The User instance if found, None otherwise
        """
        return self.db.query(models.User).filter(
            models.User.email == email
        ).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[models.User]:
        """
        Retrieve all users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of User instances
        """
        return self.db.query(models.User).offset(skip).limit(limit).all()

    def create(self, user: schemas.User_Create) -> models.User:
        """
        Create a new user with hashed password.

        Args:
            user: The user creation schema

        Returns:
            The created User instance
        """
        db_user = models.User(
            user_name=user.user_name,
            hashed_password=self._get_password_hash(user.password),
            email=user.email
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def email_exists(self, email: str) -> bool:
        """
        Check if an email is already registered.

        Args:
            email: The email to check

        Returns:
            True if email exists, False otherwise
        """
        return self.get_by_email(email) is not None

    def username_exists(self, username: str) -> bool:
        """
        Check if a username is already taken.

        Args:
            username: The username to check

        Returns:
            True if username exists, False otherwise
        """
        return self.get_by_username(username) is not None

    def authenticate(self, username: str, password: str) -> models.User | None:
        """
        Authenticate a user by username/email and password.

        Args:
            username: The username or email
            password: The plain text password

        Returns:
            The User instance if authentication succeeds, None otherwise
        """
        user = self.get_by_username(username)
        if not user:
            user = self.get_by_email(username)

        if not user:
            return None

        if not self._verify_password(password, user.hashed_password):
            return None

        return user

    def update_password(self, user: models.User, new_password: str) -> models.User:
        """
        Update a user's password.

        Args:
            user: The user instance to update
            new_password: The new plain text password

        Returns:
            The updated User instance
        """
        user.hashed_password = self._get_password_hash(new_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_image(self, user: models.User, image_path: str) -> models.User:
        """
        Update a user's profile image.

        Args:
            user: The user instance to update
            image_path: The new image path

        Returns:
            The updated User instance
        """
        user.user_image = image_path
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        """
        Delete a user by their ID.

        Args:
            user_id: The user's primary key

        Returns:
            True if deleted, False if not found
        """
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False

    @staticmethod
    def _verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password: The plain text password
            hashed_password: The hashed password to check against

        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def _get_password_hash(password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: The plain text password

        Returns:
            The hashed password
        """
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: timedelta,
        secret_key: str,
        algorithm: str = "HS256"
    ) -> str:
        """
        Create a JWT access token.

        Args:
            data: The data to encode in the token
            expires_delta: Token expiration time
            secret_key: The secret key for encoding
            algorithm: The encoding algorithm

        Returns:
            The encoded JWT token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta if expires_delta else datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
        return encoded_jwt
