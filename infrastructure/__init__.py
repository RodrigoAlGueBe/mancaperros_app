"""
Infrastructure layer for the application.

This package contains all infrastructure-related code including:
- Database configuration and session management
- Repository implementations
- External service integrations
"""

from infrastructure.database import SessionLocal, engine, Base, get_db

__all__ = [
    "SessionLocal",
    "engine",
    "Base",
    "get_db",
]
