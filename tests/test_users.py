"""
User endpoint tests.

Tests cover:
- Get user by email
- Get all users
- Get current user info
- User main page information
- User authorization checks
- User data validation

All tests use in-memory SQLite database via conftest.py fixtures.
"""

import pytest
from fastapi import status


class TestGetUserByEmail:
    """Test suite for GET /api/v1/users/get_user_by_email/{user_email}"""

    def test_get_user_by_email_success(self, client, test_user, auth_headers):
        """
        Test successful retrieval of user by email.

        Validates that:
        - Can retrieve own user information by email
        - Returns correct user data
        - Response includes all expected fields
        """
        response = client.get(
            f"/api/v1/users/get_user_by_email/{test_user.email}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["user_name"] == test_user.user_name
        assert data["user_id"] == test_user.user_id

    def test_get_user_by_email_not_found(self, client, auth_headers):
        """
        Test retrieval fails with non-existent email.

        Validates that:
        - Returns 403 Forbidden for non-existent or unauthorized email
        - Error message indicates not authorized
        """
        response = client.get(
            "/api/v1/users/get_user_by_email/nonexistent@example.com",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not authorized to access this user's data" in response.json()["error"]["message"]

    def test_get_user_by_email_unauthorized_access(self, client, test_user, second_test_user, auth_headers):
        """
        Test user cannot access another user's data by email.

        Validates that:
        - Users cannot view other users' data
        - Returns 403 Forbidden
        """
        # Try to access second_test_user's data with test_user's token
        response = client.get(
            f"/api/v1/users/get_user_by_email/{second_test_user.email}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not authorized to access this user's data" in response.json()["error"]["message"]

    def test_get_user_by_email_without_auth(self, client, test_db, test_user):
        """
        Test retrieval fails without authentication.

        Validates that:
        - Endpoint requires authentication
        - Returns 401 Unauthorized
        """
        response = client.get(f"/api/v1/users/get_user_by_email/{test_user.email}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetAllUsers:
    """Test suite for GET /api/v1/users/"""

    def test_get_all_users_success(self, client, test_user, second_test_user, auth_headers):
        """
        Test successful retrieval of all users.

        Validates that:
        - Returns list of all users in database
        - Response includes all created users
        - All users have required fields
        """
        response = client.get("/api/v1/users/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 2  # test_user and second_test_user

        # Verify both users are in response
        emails = [user["email"] for user in data]
        assert test_user.email in emails
        assert second_test_user.email in emails

    def test_get_all_users_empty_database(self, client, test_db, test_user, auth_headers):
        """
        Test get all users returns list even with only one user.

        Note: This endpoint returns users successfully if any exist.
        The database has the test_user needed for authentication.
        An truly empty database cannot be tested with authentication.
        """
        response = client.get("/api/v1/users/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 1  # At least test_user exists

    def test_get_all_users_without_auth(self, client, test_db):
        """
        Test retrieval fails without authentication.

        Validates that:
        - Endpoint requires authentication
        - Returns 401 Unauthorized
        """
        response = client.get("/api/v1/users/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetCurrentUser:
    """Test suite for GET /api/v1/users/me"""

    def test_get_current_user_success(self, client, test_user, auth_headers):
        """
        Test successful retrieval of current authenticated user.

        Validates that:
        - Authenticated user can get their own information
        - Returns correct user data
        - Requires valid authentication token
        """
        response = client.get("/api/v1/users/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["user_name"] == test_user.user_name
        assert data["user_id"] == test_user.user_id

    def test_get_current_user_without_auth(self, client, test_db):
        """
        Test get current user fails without authentication.

        Validates that:
        - Endpoint requires authentication
        - Returns 401 Unauthorized without token
        """
        response = client.get("/api/v1/users/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_with_invalid_token(self, client, invalid_token):
        """
        Test get current user fails with invalid token.

        Validates that:
        - Invalid token is rejected
        - Returns 401 Unauthorized
        """
        headers = {"Authorization": f"Bearer {invalid_token}"}
        response = client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetUserMainPageInfo:
    """Test suite for GET /api/v1/users/main_page_info"""

    def test_get_user_main_page_info_without_exercise_plan(self, client, test_user, auth_headers):
        """
        Test get main page info for user without exercise plan.

        Validates that:
        - Returns user basic information
        - Exercise plan fields are None when no plan assigned
        - Response includes all required fields
        """
        response = client.get("/api/v1/users/main_page_info", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_name"] == test_user.user_name
        assert data["email"] == test_user.email
        assert "user_image" in data
        assert data["exercise_plan_name"] is None
        assert data["exercise_plan_id"] is None

    def test_get_user_main_page_info_with_exercise_plan(self, client, test_user, assigned_exercise_plan, auth_headers):
        """
        Test get main page info for user with assigned exercise plan.

        Validates that:
        - Returns user information including exercise plan details
        - Exercise plan name and ID are populated
        """
        response = client.get("/api/v1/users/main_page_info", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_name"] == test_user.user_name
        assert data["email"] == test_user.email
        assert data["exercise_plan_name"] is not None
        assert data["exercise_plan_id"] is not None

    def test_get_user_main_page_info_without_auth(self, client, test_db):
        """
        Test get main page info fails without authentication.

        Validates that:
        - Endpoint requires authentication
        - Returns 401 Unauthorized
        """
        response = client.get("/api/v1/users/main_page_info")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserExercisePlans:
    """Test suite for GET /api/v1/users/{user_id}/exercise_plans"""

    def test_get_user_exercise_plans_success(self, client, test_user, assigned_exercise_plan, auth_headers):
        """
        Test successful retrieval of user's exercise plans.

        Validates that:
        - Returns list of exercise plans for the user
        - User can access their own plans
        """
        response = client.get(
            f"/api/v1/users/{test_user.user_id}/exercise_plans",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_user_exercise_plans_unauthorized(self, client, test_user, second_test_user, auth_headers):
        """
        Test user cannot access another user's exercise plans.

        Validates that:
        - Users cannot view other users' data
        - Returns 401 Unauthorized for unauthorized access
        """
        # Try to access second_test_user's plans with test_user's token
        response = client.get(
            f"/api/v1/users/{second_test_user.user_id}/exercise_plans",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authorizated to use this user" in response.json()["error"]["message"]

    def test_get_user_exercise_plans_without_auth(self, client, test_db, test_user):
        """
        Test retrieval fails without authentication.

        Validates that:
        - Endpoint requires authentication
        - Returns 401 Unauthorized
        """
        response = client.get(f"/api/v1/users/{test_user.user_id}/exercise_plans")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserDataValidation:
    """Test suite for user data validation"""

    def test_user_email_unique_constraint(self, client, test_db, test_user):
        """
        Test email uniqueness is enforced.

        Validates that:
        - Cannot create user with duplicate email
        - Database constraint is enforced
        """
        duplicate_user = {
            "user_name": "different_username",
            "email": test_user.email,  # Duplicate email
            "password": "password123"
        }

        response = client.post("/api/v1/users/", json=duplicate_user)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["error"]["message"]

    def test_user_username_unique_constraint(self, client, test_db, test_user):
        """
        Test username uniqueness is enforced.

        Validates that:
        - Cannot create user with duplicate username
        - Database constraint is enforced
        """
        duplicate_user = {
            "user_name": test_user.user_name,  # Duplicate username
            "email": "different@example.com",
            "password": "password123"
        }

        response = client.post("/api/v1/users/", json=duplicate_user)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username already exist" in response.json()["error"]["message"]

    def test_user_password_hashed(self, test_db, test_user):
        """
        Test that password is properly hashed in database.

        Validates that:
        - Password is not stored in plain text
        - Hashed password is different from plain password
        - Password hash is valid bcrypt format
        """
        assert test_user.hashed_password != test_user.plain_password
        assert test_user.hashed_password.startswith("$2b$")  # bcrypt prefix
        assert len(test_user.hashed_password) > 50  # Hashed passwords are long


# Run tests with: pytest tests/test_users.py -v
