"""
Pytest configuration and shared fixtures for test suite.

This module provides:
- Database fixtures (in-memory SQLite for tests)
- TestClient for API testing
- Pre-created test users with authentication
- JWT token generation for protected endpoint testing
- Exercise plan and routine fixtures

All fixtures are function-scoped to ensure test isolation.
"""

import os
# Set TESTING environment variable BEFORE importing application modules
os.environ["TESTING"] = "1"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import timedelta

# Import from main application (after TESTING is set)
from database import Base
from main import app
from app.api.v1.dependencies import get_db
from app.core.config import settings
from app.core.security import create_access_token
import models
import crud
import schemas


# ==================== DATABASE FIXTURES ====================

@pytest.fixture(scope="function")
def test_db():
    """
    Create a temporary file-based SQLite database for testing.

    This fixture:
    - Creates a new database file for each test
    - Automatically creates all tables
    - Cleans up after test completes
    - Ensures test isolation (no shared state between tests)
    - Uses file-based DB to support TestClient threading

    Yields:
        Session: SQLAlchemy database session
    """
    import tempfile
    import os

    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
        # Clean up temp file
        os.close(db_fd)
        os.unlink(db_path)


@pytest.fixture(scope="function")
def client(test_db):
    """
    Create a TestClient with test database dependency override.

    This fixture:
    - Overrides the get_db dependency to use test database
    - Provides a TestClient for making HTTP requests
    - Automatically handles database cleanup

    Args:
        test_db: Test database session fixture

    Yields:
        TestClient: FastAPI test client
    """
    def override_get_db():
        return test_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides after test
    app.dependency_overrides.clear()


# ==================== USER FIXTURES ====================

@pytest.fixture(scope="function")
def test_user(test_db):
    """
    Create a test user in the database.

    Creates a user with known credentials for authentication testing:
    - Username: testuser
    - Email: testuser@example.com
    - Password: testpassword123

    Args:
        test_db: Test database session fixture

    Returns:
        models.User: Created user object with hashed password
    """
    user_data = schemas.User_Create(
        user_name="testuser",
        email="testuser@example.com",
        password="testpassword123"
    )

    user = crud.create_user(db=test_db, user=user_data)
    # Store plain password for testing
    user.plain_password = "testpassword123"

    return user


@pytest.fixture(scope="function")
def second_test_user(test_db):
    """
    Create a second test user for authorization testing.

    Used to test that users cannot access other users' data.

    Args:
        test_db: Test database session fixture

    Returns:
        models.User: Second test user object
    """
    user_data = schemas.User_Create(
        user_name="testuser2",
        email="testuser2@example.com",
        password="testpassword456"
    )

    user = crud.create_user(db=test_db, user=user_data)
    user.plain_password = "testpassword456"

    return user


# ==================== AUTHENTICATION FIXTURES ====================

@pytest.fixture(scope="function")
def auth_token(test_user):
    """
    Generate a valid JWT token for test user.

    Creates an access token that can be used for testing protected endpoints.

    Args:
        test_user: Test user fixture

    Returns:
        str: Valid JWT access token
    """
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": test_user.email},
        expires_delta=access_token_expires
    )

    return access_token


@pytest.fixture(scope="function")
def auth_headers(auth_token):
    """
    Generate authorization headers with valid JWT token.

    Provides headers dictionary ready to use in requests to protected endpoints.

    Args:
        auth_token: Valid JWT token fixture

    Returns:
        dict: Headers dictionary with Bearer token
    """
    return {
        "Authorization": f"Bearer {auth_token}"
    }


@pytest.fixture(scope="function")
def second_user_auth_token(second_test_user):
    """
    Generate a valid JWT token for second test user.

    Args:
        second_test_user: Second test user fixture

    Returns:
        str: Valid JWT access token for second user
    """
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": second_test_user.email},
        expires_delta=access_token_expires
    )

    return access_token


@pytest.fixture(scope="function")
def second_user_auth_headers(second_user_auth_token):
    """
    Generate authorization headers for second test user.

    Args:
        second_user_auth_token: Valid JWT token for second user

    Returns:
        dict: Headers dictionary with Bearer token
    """
    return {
        "Authorization": f"Bearer {second_user_auth_token}"
    }


@pytest.fixture(scope="function")
def expired_token(test_user):
    """
    Generate an expired JWT token for testing token expiration.

    Args:
        test_user: Test user fixture

    Returns:
        str: Expired JWT access token
    """
    # Create token that expired 1 hour ago
    access_token_expires = timedelta(minutes=-60)
    expired_token = create_access_token(
        data={"sub": test_user.email},
        expires_delta=access_token_expires
    )

    return expired_token


@pytest.fixture(scope="function")
def invalid_token():
    """
    Generate an invalid JWT token for testing token validation.

    Returns:
        str: Invalid JWT token (malformed)
    """
    return "invalid.jwt.token.that.should.fail"


# ==================== EXERCISE PLAN FIXTURES ====================

@pytest.fixture(scope="function")
def test_exercise_plan_global(test_db, test_user):
    """
    Create a global exercise plan for testing.

    Args:
        test_db: Test database session fixture
        test_user: Test user fixture (creator)

    Returns:
        models.Exercise_plan_global: Created global exercise plan
    """
    plan_data = schemas.Exercise_plan_global_Create(
        exercise_plan_name="Test Full Body Plan",
        exercise_plan_type="full_body",
        difficult_level="beginner"
    )

    plan = crud.create_exercise_plan_global(
        db=test_db,
        exercise_plan=plan_data,
        user_id=test_user.user_id
    )

    return plan


@pytest.fixture(scope="function")
def test_routine_global(test_db, test_exercise_plan_global):
    """
    Create a global routine for testing.

    Args:
        test_db: Test database session fixture
        test_exercise_plan_global: Test exercise plan fixture

    Returns:
        models.Rutine_global: Created global routine
    """
    routine_data = schemas.Rutine_global_Create(
        rutine_name="Test Chest Routine",
        rutine_type="strength",
        rutine_group="chest",
        rutine_category="push",
        exercise_plan_id=test_exercise_plan_global.exercise_plan_id,
        rst_btw_exercises="60",
        rst_btw_rounds="120",
        difficult_level="beginner",
        rounds=3
    )

    routine = crud.create_routine_global(db=test_db, rutine_gobal=routine_data)

    return routine


@pytest.fixture(scope="function")
def test_exercise_global(test_db, test_routine_global):
    """
    Create a global exercise for testing.

    Args:
        test_db: Test database session fixture
        test_routine_global: Test routine fixture

    Returns:
        models.Exsercise_global: Created global exercise
    """
    exercise_data = schemas.Exercise_global_Create(
        exercise_name="Push-ups",
        rep="10",
        exercise_type="push-bodyweight",
        exercise_group="chest",
        rutine_id=test_routine_global.rutine_id,
        image="pushups.jpg"
    )

    exercise = crud.create_exercise_global(db=test_db, exercise_global=exercise_data)

    return exercise


@pytest.fixture(scope="function")
def assigned_exercise_plan(test_db, test_user, test_exercise_plan_global, test_routine_global, test_exercise_global):
    """
    Create an assigned exercise plan for user with complete data.

    This fixture provides a fully set up exercise plan assigned to a user,
    including routines and exercises.

    Args:
        test_db: Test database session fixture
        test_user: Test user fixture
        test_exercise_plan_global: Test exercise plan fixture
        test_routine_global: Test routine fixture
        test_exercise_global: Test exercise fixture

    Returns:
        models.Exercise_plan: Assigned exercise plan
    """
    # Assign plan to user
    assigned_plan = crud.asign_exercise_plan(
        db=test_db,
        exercise_plan=test_exercise_plan_global,
        user_id=test_user.user_id
    )

    # Record start of exercise plan
    crud.record_start_exercise_plan(test_db, test_user.user_id, test_exercise_plan_global)

    return assigned_plan


# ==================== UTILITY FIXTURES ====================

@pytest.fixture(scope="function")
def clean_database(test_db):
    """
    Ensure database is clean before test runs.

    Useful for tests that need to verify empty state.

    Args:
        test_db: Test database session fixture
    """
    # Database is already clean from test_db fixture
    # This is a placeholder for additional cleanup if needed
    yield test_db
