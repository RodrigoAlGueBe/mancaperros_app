"""
Test suite for Mancaperros FastAPI application.

This package contains comprehensive tests for:
- Authentication endpoints (login, JWT token validation)
- User management (registration, user retrieval)
- Security (protected endpoints, authorization)
- Configuration (settings validation)

All tests use SQLite in-memory database to avoid affecting production data.

To run tests:
    pytest                           # Run all tests
    pytest tests/test_auth.py        # Run specific test file
    pytest -v                        # Verbose output
    pytest --cov=.                   # Run with coverage report
    pytest -k "test_login"           # Run tests matching pattern
"""
