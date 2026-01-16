"""
Custom exceptions for the Mancaperros API.

This module defines custom exception classes that provide consistent
error handling across the application. Each exception maps to a specific
HTTP status code and includes a structured error response format.

Usage:
    from app.core.exceptions import NotFoundException, BadRequestException

    raise NotFoundException("User", "user_id", 123)
    raise BadRequestException("Email already registered")
"""

from typing import Any, Optional


class APIException(Exception):
    """
    Base exception class for all API exceptions.

    All custom exceptions should inherit from this class to ensure
    consistent error response format across the application.

    Attributes:
        status_code: HTTP status code to return
        code: Machine-readable error code (e.g., "NOT_FOUND")
        message: Human-readable error message
        details: Optional additional error details
    """

    status_code: int = 500
    code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None
    ):
        self.message = message
        self.details = details
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to error response dictionary."""
        error = {
            "code": self.code,
            "message": self.message,
        }
        if self.details:
            error["details"] = self.details
        return {"error": error}


class NotFoundException(APIException):
    """
    Exception raised when a requested resource is not found.

    HTTP Status: 404 Not Found

    Example:
        raise NotFoundException("User", "id", 123)
        # Response: {"error": {"code": "NOT_FOUND", "message": "User with id=123 not found"}}

        raise NotFoundException("No active exercise plan found")
        # Response: {"error": {"code": "NOT_FOUND", "message": "No active exercise plan found"}}
    """

    status_code = 404
    code = "NOT_FOUND"

    def __init__(
        self,
        resource: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[dict[str, Any]] = None
    ):
        if field and value is not None:
            message = f"{resource} with {field}={value} not found"
        else:
            message = resource
        super().__init__(message, details)


class UnauthorizedException(APIException):
    """
    Exception raised when authentication fails or is missing.

    HTTP Status: 401 Unauthorized

    This should be used when:
    - No authentication credentials provided
    - Invalid or expired token
    - Invalid username/password

    Example:
        raise UnauthorizedException("Invalid or expired token")
        raise UnauthorizedException("Incorrect username or password")
    """

    status_code = 401
    code = "UNAUTHORIZED"

    def __init__(
        self,
        message: str = "Authentication required",
        details: Optional[dict[str, Any]] = None
    ):
        super().__init__(message, details)


class ForbiddenException(APIException):
    """
    Exception raised when user is authenticated but not authorized.

    HTTP Status: 403 Forbidden

    This should be used when:
    - User is logged in but doesn't have permission
    - Trying to access another user's resources
    - Admin-only endpoint accessed by regular user

    Example:
        raise ForbiddenException("Not authorized to access this user's data")
        raise ForbiddenException("Admin access required")
    """

    status_code = 403
    code = "FORBIDDEN"

    def __init__(
        self,
        message: str = "Access denied",
        details: Optional[dict[str, Any]] = None
    ):
        super().__init__(message, details)


class BadRequestException(APIException):
    """
    Exception raised when the request is malformed or invalid.

    HTTP Status: 400 Bad Request

    This should be used when:
    - Invalid input data
    - Business rule validation fails
    - Required fields missing

    Example:
        raise BadRequestException("Email already registered")
        raise BadRequestException("Invalid exercise plan type")
    """

    status_code = 400
    code = "BAD_REQUEST"

    def __init__(
        self,
        message: str = "Invalid request",
        details: Optional[dict[str, Any]] = None
    ):
        super().__init__(message, details)


class ConflictException(APIException):
    """
    Exception raised when there's a conflict with the current state.

    HTTP Status: 409 Conflict

    This should be used when:
    - Resource already exists (duplicate)
    - State conflict prevents operation
    - Concurrent modification issues

    Example:
        raise ConflictException("Username already exists")
        raise ConflictException("Routine name already exists for this exercise plan")
    """

    status_code = 409
    code = "CONFLICT"

    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[dict[str, Any]] = None
    ):
        super().__init__(message, details)


class ValidationException(APIException):
    """
    Exception raised when input validation fails.

    HTTP Status: 422 Unprocessable Entity

    This is used for semantic validation errors where the request
    syntax is correct but the content is invalid.

    Example:
        raise ValidationException(
            "Validation failed",
            details={"email": "Invalid email format", "age": "Must be positive"}
        )
    """

    status_code = 422
    code = "VALIDATION_ERROR"

    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[dict[str, Any]] = None
    ):
        super().__init__(message, details)


class DatabaseException(APIException):
    """
    Exception raised when a database operation fails.

    HTTP Status: 500 Internal Server Error

    This wraps SQLAlchemy and other database errors.
    The original error details should be logged but not exposed to clients.

    Example:
        raise DatabaseException("Failed to save user")
    """

    status_code = 500
    code = "DATABASE_ERROR"

    def __init__(
        self,
        message: str = "Database operation failed",
        details: Optional[dict[str, Any]] = None
    ):
        super().__init__(message, details)
