"""
API v1 router aggregator.

This module aggregates all v1 endpoint routers into a single router
that can be included in the main application.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, exercises, routines, health


api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(exercises.router)
api_router.include_router(routines.router)

# Health router is included separately without prefix
# to be mounted at root level in main.py
health_router = health.router
