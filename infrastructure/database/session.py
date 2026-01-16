"""
Database session configuration module.

This module configures SQLAlchemy database connection using centralized
settings from config.py. Provides session management and dependency injection
for FastAPI endpoints.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from config import settings


# Create engine using database URL from settings
# SQLite requires check_same_thread=False for FastAPI compatibility
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.use_sqlite else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.

    Yields a database session and ensures it is closed after use.
    Use with FastAPI's Depends() for dependency injection.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
