"""
Authentication endpoints.

This module contains endpoints for user authentication including:
- Login (token generation)
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_db
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token, verify_password
from jose import JWTError
import crud
import models
import schemas


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login.

    Authenticate user with username/email and password, return an access token.

    Args:
        form_data: OAuth2 form containing username and password
        db: Database session

    Returns:
        Token: Object containing access_token and token_type

    Raises:
        HTTPException: 400 if user not found, 401 if credentials are invalid
    """
    # Try to find user by email first, then by username
    user_db = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()

    if not user_db:
        user_db = db.query(models.User).filter(
            models.User.user_name == form_data.username
        ).first()

    if not user_db:
        raise HTTPException(status_code=400, detail="No user found")

    # Authenticate user
    user = crud.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    # Create refresh token
    refresh_token = create_refresh_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=schemas.Token)
async def refresh_access_token(
    token_request: schemas.RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh an access token using a valid refresh token.

    Args:
        token_request: Request body containing the refresh_token
        db: Database session

    Returns:
        Token: Object containing new access_token, refresh_token and token_type

    Raises:
        HTTPException: 401 if refresh token is invalid, expired, or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and validate refresh token
        payload = decode_token(token_request.refresh_token)

        # Verify it's a refresh token
        token_type = payload.get("type")
        if token_type != "refresh":
            raise credentials_exception

        # Get user email from token
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Verify user exists
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception

    # Create new tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
