"""
Mancaperros API - Main Application Entry Point.

This module initializes the FastAPI application, configures middleware,
exception handlers, and includes all API routers. All endpoint logic has
been moved to app/api/v1/endpoints/ for better organization and maintainability.
"""

import logging
import os
import traceback

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.router import api_router, health_router
from app.core.config import settings
from app.core.exceptions import APIException
import models


# Create database tables only if not in testing mode
if not os.getenv("TESTING"):
    from database import engine
    models.Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="API for Mancaperros fitness application",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ======================== EXCEPTION HANDLERS ========================

@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """
    Handler for custom API exceptions.
    Returns structured error response with appropriate status code.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handler for Starlette/FastAPI HTTP exceptions.
    Converts to consistent error response format.
    """
    # Map status codes to error codes
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_ERROR",
    }
    error_code = code_map.get(exc.status_code, "HTTP_ERROR")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": error_code,
                "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail)
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler for FastAPI request validation errors.
    Returns 422 with structured error details.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error.get("loc", [])),
            "message": error.get("msg", "Validation error")
        })

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": errors
            }
        }
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Handler for Pydantic validation errors.
    Returns 422 with structured error details.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error.get("loc", [])),
            "message": error.get("msg", "Validation error")
        })

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": errors
            }
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handler for SQLAlchemy database errors.
    Logs the full error but returns generic message to client.
    """
    logger.error(
        f"Database error on {request.method} {request.url.path}: {str(exc)}",
        exc_info=True
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "DATABASE_ERROR",
                "message": "A database error occurred"
            }
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for unhandled exceptions.
    Logs full traceback and returns generic 500 error.
    """
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}:\n"
        f"{traceback.format_exc()}"
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        }
    )


# ======================== MIDDLEWARE CONFIGURATION ========================

# Proxy headers middleware for proper forwarding behind reverse proxies
app.add_middleware(ProxyHeadersMiddleware)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# ======================== ROUTER INCLUSION ========================

# Include health/utility endpoints at root level
app.include_router(health_router)

# Include API v1 router with prefix
app.include_router(api_router, prefix="/api/v1")
