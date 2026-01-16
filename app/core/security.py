"""
Security utilities for authentication and authorization.

This module contains all security-related functions including:
- Password hashing and verification
- JWT token creation and validation
- Authentication utilities
"""

from datetime import UTC, datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against

    Returns:
        True if the password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: The plain text password to hash

    Returns:
        The hashed password
    """
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    secret_key: Optional[str] = None,
    algorithm: Optional[str] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: The data to encode in the token (typically contains 'sub' with user identifier)
        expires_delta: Optional custom expiration time. Defaults to settings.access_token_expire_minutes
        secret_key: Optional custom secret key. Defaults to settings.secret_key
        algorithm: Optional custom algorithm. Defaults to settings.algorithm

    Returns:
        The encoded JWT token as a string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jwt.encode(
        to_encode,
        secret_key or settings.secret_key,
        algorithm=algorithm or settings.algorithm
    )

    return encoded_jwt


def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    secret_key: Optional[str] = None,
    algorithm: Optional[str] = None
) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: The data to encode in the token (typically contains 'sub' with user identifier)
        expires_delta: Optional custom expiration time. Defaults to settings.refresh_token_expire_days
        secret_key: Optional custom secret key. Defaults to settings.secret_key
        algorithm: Optional custom algorithm. Defaults to settings.algorithm

    Returns:
        The encoded JWT refresh token as a string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)

    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode,
        secret_key or settings.secret_key,
        algorithm=algorithm or settings.algorithm
    )

    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    Args:
        token: The JWT token to decode

    Returns:
        The decoded token payload

    Raises:
        JWTError: If the token is invalid or expired
    """
    return jwt.decode(
        token=token,
        key=settings.secret_key,
        algorithms=[settings.algorithm]
    )
