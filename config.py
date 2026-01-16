"""
Centralized configuration module using Pydantic Settings.

This module provides a secure, validated configuration system that reads
from environment variables and .env files. All sensitive credentials
should be defined in environment variables, NEVER hardcoded.

Usage:
    from config import settings

    # Access configuration values
    db_url = settings.database_url
    secret = settings.secret_key

Environment:
    - Development: Uses .env file with DEBUG=true
    - Production: Uses environment variables with DEBUG=false
"""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden by environment variables.
    Variable names are case-insensitive (automatically converted to uppercase).

    Required variables in production:
        - SECRET_KEY: Must be set to a secure random value
        - DB_PASSWORD: Database password (never use default in production)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables
    )

    # ======================== APPLICATION SETTINGS ========================

    app_name: str = Field(
        default="Mancaperros App",
        description="Application display name"
    )

    version: str = Field(
        default="1.0.0",
        description="Application version"
    )

    debug: bool = Field(
        default=False,
        description="Enable debug mode (set to True for development)"
    )

    environment: str = Field(
        default="production",
        description="Environment name: 'development', 'staging', or 'production'"
    )

    # ======================== SECURITY SETTINGS ========================

    secret_key: str = Field(
        default="CHANGE_ME_IN_PRODUCTION_USE_SECURE_RANDOM_KEY",
        description="Secret key for JWT token signing. Generate with: openssl rand -hex 32"
    )

    algorithm: str = Field(
        default="HS256",
        description="Algorithm used for JWT encoding"
    )

    access_token_expire_minutes: int = Field(
        default=30,  # SECURITY: Reduced to 30 minutes (OWASP recommendation)
        ge=1,
        le=60,  # SECURITY: Max 1 hour for security best practices
        description="JWT access token expiration time in minutes (recommended: 15-30)"
    )

    # ======================== DATABASE SETTINGS ========================

    db_user: str = Field(
        default="root",
        description="Database username"
    )

    db_password: str = Field(
        default="",
        description="Database password - MUST be set via environment variable"
    )

    db_host: str = Field(
        default="localhost",
        description="Database host address"
    )

    db_port: str = Field(
        default="3306",
        description="Database port"
    )

    db_name: str = Field(
        default="mancaperros",
        description="Database name"
    )

    # SQLite fallback for local development
    use_sqlite: bool = Field(
        default=False,
        description="Use SQLite instead of MySQL (for local development only)"
    )

    sqlite_url: str = Field(
        default="sqlite:///./mancaperros_app.db",
        description="SQLite database URL for local development"
    )

    # ======================== CORS SETTINGS ========================

    cors_origins: List[str] = Field(
        default=[
            "http://localhost",
            "http://localhost:8080",
            "http://localhost:3100",
            "http://localhost:5173",
        ],
        description="List of allowed CORS origins"
    )

    cors_allow_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS requests"
    )

    cors_allow_methods: List[str] = Field(
        default=["*"],
        description="Allowed HTTP methods for CORS"
    )

    cors_allow_headers: List[str] = Field(
        default=["*"],
        description="Allowed HTTP headers for CORS"
    )

    # ======================== APPLICATION DEFAULTS ========================

    routine_group_order_default: str = Field(
        default='["chest", "back", "shoulders", "legs"]',
        description="Default order of routine muscle groups as JSON string"
    )

    # ======================== COMPUTED PROPERTIES ========================

    @computed_field
    @property
    def database_url(self) -> str:
        """
        Build the complete database URL from components.

        Returns SQLite URL if use_sqlite is True, otherwise builds MySQL URL.
        Uses urllib.parse.quote_plus for special characters in credentials.
        """
        if self.use_sqlite:
            return self.sqlite_url

        import urllib.parse

        # URL-encode user and password to handle special characters
        user = urllib.parse.quote_plus(self.db_user)
        password = urllib.parse.quote_plus(self.db_password)

        return f"mysql+pymysql://{user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @computed_field
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @computed_field
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    # ======================== VALIDATORS ========================

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of the allowed values."""
        allowed = {"development", "staging", "production"}
        if v.lower() not in allowed:
            raise ValueError(f"environment must be one of: {allowed}")
        return v.lower()

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key is secure."""
        import os
        if v == "CHANGE_ME_IN_PRODUCTION_USE_SECURE_RANDOM_KEY":
            env = os.getenv("ENVIRONMENT", "development")
            if env.lower() == "production":
                raise ValueError(
                    "SECRET_KEY must be set in production! "
                    "Generate with: openssl rand -hex 32"
                )
            import warnings
            warnings.warn(
                "Using default SECRET_KEY! This is insecure for production.",
                UserWarning,
                stacklevel=2
            )
        elif len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """
        Parse CORS origins from string or list.

        Supports:
            - List of strings: ["http://localhost", "http://example.com"]
            - Comma-separated string: "http://localhost,http://example.com"
            - JSON array string: '["http://localhost", "http://example.com"]'
        """
        if isinstance(v, str):
            # Try parsing as JSON first
            if v.startswith("["):
                import json
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # Fall back to comma-separated
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Uses lru_cache to ensure settings are only loaded once.
    Call get_settings.cache_clear() to reload settings if needed.

    Returns:
        Settings: The application settings instance
    """
    return Settings()


# Global settings instance for easy import
settings = get_settings()
