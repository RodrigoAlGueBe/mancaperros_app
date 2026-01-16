"""
Database configuration module.

This module configures SQLAlchemy database connection using centralized
settings from config.py. No credentials are hardcoded here.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings

# Import Base from the centralized location (used by all models)
from infrastructure.database.models.base import Base

# Create engine using database URL from settings
# SQLite requires check_same_thread=False for FastAPI compatibility
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.use_sqlite else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
