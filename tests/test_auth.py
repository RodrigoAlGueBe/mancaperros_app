"""
Authentication endpoint tests.

Tests cover:
- User registration (public endpoint)
- Login with valid/invalid credentials
- Token generation and validation
- Token expiration handling
- Email and username uniqueness constraints

All tests use in-memory SQLite database via conftest.py fixtures.
"""

import pytest
from fastapi import status


class TestUserRegistration:
    """Test suite for user registration endpoint POST /api/v1/users/"""

    def test_create_user_success(self, client, test_db):
        """
        Test successful user registration.

        Validates that:
        - User can register with valid data
        - Response returns 201 Created status
        - Success message is returned
        """
        user_data = {
            "user_name": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword123"
        }

        response = client.post("/api/v1/users/", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["detail"] == "User created correctly"

    def test_create_user_duplicate_email(self, client, test_user):
        """
        Test registration fails with duplicate email.

        Validates that:
        - Cannot register with email already in use
        - Returns 400 Bad Request
        - Error message indicates email already registered
        """
        user_data = {
            "user_name": "anotheruser",
            "email": test_user.email,  # Duplicate email
            "password": "password123"
        }

        response = client.post("/api/v1/users/", json=user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["error"]["message"]

    def test_create_user_duplicate_username(self, client, test_user):
        """
        Test registration fails with duplicate username.

        Validates that:
        - Cannot register with username already in use
        - Returns 400 Bad Request
        - Error message indicates username already exists
        """
        user_data = {
            "user_name": test_user.user_name,  # Duplicate username
            "email": "different@example.com",
            "password": "password123"
        }

        response = client.post("/api/v1/users/", json=user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username already exist" in response.json()["error"]["message"]

    def test_create_user_invalid_email_format(self, client, test_db):
        """
        Test registration with invalid email format.

        Note: Current schema accepts any string as email.
        This test creates user successfully with invalid email format.
        Email validation should be implemented using EmailStr in schema.
        """
        user_data = {
            "user_name": "testuser",
            "email": "not-a-valid-email",  # Invalid email format but accepted
            "password": "password123"
        }

        response = client.post("/api/v1/users/", json=user_data)

        # Currently accepts invalid email format (schema uses str not EmailStr)
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_user_missing_required_fields(self, client, test_db):
        """
        Test registration fails when required fields are missing.

        Validates that:
        - All required fields must be provided
        - Returns 422 Unprocessable Entity
        """
        user_data = {
            "user_name": "testuser"
            # Missing email and password
        }

        response = client.post("/api/v1/users/", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    """Test suite for login endpoint POST /api/v1/auth/token"""

    def test_login_success_with_email(self, client, test_user):
        """
        Test successful login with email.

        Validates that:
        - User can login with email and password
        - Returns 200 status
        - Returns access_token and token_type
        - Token type is 'bearer'
        """
        login_data = {
            "username": test_user.email,  # OAuth2 uses 'username' field
            "password": test_user.plain_password
        }

        response = client.post("/api/v1/auth/token", data=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_success_with_username(self, client, test_user):
        """
        Test successful login with username.

        Validates that:
        - User can login with username instead of email
        - Returns valid JWT token
        """
        login_data = {
            "username": test_user.user_name,
            "password": test_user.plain_password
        }

        response = client.post("/api/v1/auth/token", data=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_password(self, client, test_user):
        """
        Test login fails with incorrect password.

        Validates that:
        - Cannot login with wrong password
        - Returns 401 Unauthorized
        - Error message indicates incorrect credentials
        """
        login_data = {
            "username": test_user.email,
            "password": "wrongpassword"
        }

        response = client.post("/api/v1/auth/token", data=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["error"]["message"]

    def test_login_nonexistent_user(self, client, test_db):
        """
        Test login fails with non-existent user.

        Validates that:
        - Cannot login with email that doesn't exist
        - Returns 400 Bad Request
        - Error message indicates user not found
        """
        login_data = {
            "username": "nonexistent@example.com",
            "password": "somepassword"
        }

        response = client.post("/api/v1/auth/token", data=login_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No user found" in response.json()["error"]["message"]

    def test_login_empty_password(self, client, test_db, test_user):
        """
        Test login fails with empty password.

        Validates that:
        - Cannot login without password
        - Returns 422 Unprocessable Entity (validation error)
        """
        login_data = {
            "username": test_user.email,
            "password": ""
        }

        response = client.post("/api/v1/auth/token", data=login_data)

        # Empty password should fail validation or authentication
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]

    def test_login_missing_credentials(self, client, test_db):
        """
        Test login fails when credentials are missing.

        Validates that:
        - Both username and password are required
        - Returns 422 Unprocessable Entity
        """
        response = client.post("/api/v1/auth/token", data={})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestTokenValidation:
    """Test suite for JWT token validation"""

    def test_valid_token_access(self, client, test_user, auth_headers):
        """
        Test valid token allows access to protected endpoint.

        Validates that:
        - Valid JWT token grants access to /api/v1/users/me
        - Returns user information correctly
        - User data matches the authenticated user
        """
        response = client.get("/api/v1/users/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["user_name"] == test_user.user_name
        assert data["user_id"] == test_user.user_id

    def test_expired_token_rejected(self, client, expired_token):
        """
        Test expired token is rejected.

        Validates that:
        - Expired JWT token is rejected
        - Returns 401 Unauthorized
        - Error message indicates credential validation failure
        """
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in response.json()["error"]["message"]

    def test_invalid_token_format_rejected(self, client, invalid_token):
        """
        Test malformed token is rejected.

        Validates that:
        - Invalid JWT format is rejected
        - Returns 401 Unauthorized
        """
        headers = {"Authorization": f"Bearer {invalid_token}"}
        response = client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in response.json()["error"]["message"]

    def test_missing_token_rejected(self, client, test_db):
        """
        Test request without token is rejected.

        Validates that:
        - Protected endpoint requires authentication
        - Returns 401 Unauthorized when no token provided
        """
        response = client.get("/api/v1/users/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_with_invalid_signature(self, client, test_db, test_user):
        """
        Test token with tampered signature is rejected.

        Validates that:
        - Token with invalid signature is rejected
        - Cannot forge tokens
        """
        # Create a token with wrong secret key
        from datetime import timedelta
        from app.core.security import create_access_token

        fake_token = create_access_token(
            data={"sub": test_user.email},
            expires_delta=timedelta(minutes=30),
            secret_key="wrong_secret_key_for_testing",
            algorithm="HS256"
        )

        headers = {"Authorization": f"Bearer {fake_token}"}
        response = client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTokenContent:
    """Test suite for JWT token payload validation"""

    def test_token_contains_user_email(self, client, test_db, test_user):
        """
        Test that generated token contains correct user email.

        Validates that:
        - Token payload includes user email in 'sub' claim
        - Token can be decoded to retrieve user information
        """
        login_data = {
            "username": test_user.email,
            "password": test_user.plain_password
        }

        response = client.post("/api/v1/auth/token", data=login_data)
        token = response.json()["access_token"]

        # Decode token to verify contents
        from jose import jwt
        from app.core.config import settings

        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

        assert payload["sub"] == test_user.email
        assert "exp" in payload  # Expiration claim should be present

    def test_token_expiration_time_set(self, client, test_db, test_user):
        """
        Test that token has proper expiration time set.

        Validates that:
        - Token includes 'exp' claim
        - Expiration time is in the future
        """
        login_data = {
            "username": test_user.email,
            "password": test_user.plain_password
        }

        response = client.post("/api/v1/auth/token", data=login_data)
        token = response.json()["access_token"]

        from jose import jwt
        from app.core.config import settings
        from datetime import UTC, datetime

        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

        assert "exp" in payload
        # Expiration should be in the future
        assert payload["exp"] > datetime.now(UTC).timestamp()


# Run tests with: pytest tests/test_auth.py -v
