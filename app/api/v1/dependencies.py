"""
Shared dependencies for API endpoints.

This module contains dependency injection functions used across
multiple endpoints, including database sessions and authentication.
"""

from typing import Annotated, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_token
from database import SessionLocal
import models


# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.

    Yields a database session and ensures it's properly closed
    after the request is completed.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> models.TokenData:
    """
    Get the current authenticated user from the JWT token.

    This dependency extracts and validates the JWT token from the
    Authorization header, then returns the token data containing
    the username.

    Args:
        token: JWT token from the Authorization header

    Returns:
        TokenData: Object containing the username from the token

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

        token_data = models.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    return token_data


# Type aliases for common dependencies
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[models.TokenData, Depends(get_current_user)]
