"""
Authentication models definition.

This module defines Pydantic models for authentication tokens.
These are not SQLAlchemy models but Pydantic schemas used for
JWT token handling.
"""

from pydantic import BaseModel


class Token(BaseModel):
    """
    Token response model.

    Attributes:
        access_token: The JWT access token string
        token_type: The type of token (typically "bearer")
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Token data model for decoded JWT payload.

    Attributes:
        username: The username extracted from the token
    """
    username: str | None = None
