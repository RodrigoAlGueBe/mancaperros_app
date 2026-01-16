"""
Health and utility endpoints.

This module contains infrastructure endpoints for monitoring and
basic connectivity verification, including:
- Root endpoint for API information
- Health check endpoint for load balancers and monitoring
"""

from fastapi import APIRouter

from app.core.config import settings


router = APIRouter(tags=["Health"])


@router.get("/", include_in_schema=False)
def root():
    """
    Root endpoint returning API information.

    Returns:
        Dictionary with API name, version, and status
    """
    return {
        "name": settings.app_name,
        "version": settings.version,
        "status": "running"
    }


@router.get("/health")
def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        Dictionary with status information
    """
    return {"status": "ok"}
