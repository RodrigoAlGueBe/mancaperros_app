"""
API v1 endpoints package.

This package contains all endpoint routers organized by domain:
- auth: Authentication and token management
- users: User registration and profile management
- exercises: Exercise plan creation and management
- routines: Routine operations and tracking
"""

from app.api.v1.endpoints import auth, users, exercises, routines

__all__ = ["auth", "users", "exercises", "routines"]
