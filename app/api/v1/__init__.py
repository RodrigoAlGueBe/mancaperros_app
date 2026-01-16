"""
API v1 package.

This package contains all v1 API endpoints organized by domain:
- auth: Authentication endpoints (login, token)
- users: User management endpoints
- exercises: Exercise plan management endpoints
- routines: Routine management endpoints
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, exercises, routines


# Create the main v1 router that includes all endpoint routers
api_router = APIRouter()

# Include all endpoint routers with their prefixes
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(exercises.router)
api_router.include_router(routines.router)


__all__ = ["api_router"]
