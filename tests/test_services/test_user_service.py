"""
User service tests.

Tests cover:
- User creation logic
- User retrieval operations
- Password hashing verification
- User validation rules

These are service-level tests focused on business logic.
"""

import pytest
from app.core.security import verify_password, get_password_hash
import crud
import schemas


class TestUserCreation:
    """Test suite for user creation logic"""

    def test_create_user_hashes_password(self, test_db):
        """
        Test that user creation properly hashes password.

        Validates that:
        - Password is hashed before storing
        - Hash is valid and verifiable
        - Plain password is not stored
        """
        user_data = schemas.User_Create(
            user_name="servicetest",
            email="servicetest@example.com",
            password="plaintextpassword"
        )

        created_user = crud.create_user(db=test_db, user=user_data)

        # Password should be hashed
        assert created_user.hashed_password != "plaintextpassword"
        assert created_user.hashed_password.startswith("$2b$")

        # Verify password hash works
        assert verify_password("plaintextpassword", created_user.hashed_password)
        assert not verify_password("wrongpassword", created_user.hashed_password)

    def test_create_multiple_users(self, test_db):
        """
        Test creating multiple users with different credentials.

        Validates that:
        - Multiple users can be created
        - Each has unique credentials
        - All have properly hashed passwords
        """
        users_data = [
            schemas.User_Create(
                user_name=f"user{i}",
                email=f"user{i}@example.com",
                password=f"password{i}"
            )
            for i in range(3)
        ]

        created_users = [crud.create_user(db=test_db, user=user) for user in users_data]

        assert len(created_users) == 3
        # Verify all have unique user_ids
        user_ids = [user.user_id for user in created_users]
        assert len(user_ids) == len(set(user_ids))

        # Verify all passwords are hashed
        for user in created_users:
            assert user.hashed_password.startswith("$2b$")


class TestUserRetrieval:
    """Test suite for user retrieval operations"""

    def test_get_user_by_id(self, test_db, test_user):
        """
        Test retrieving user by ID.

        Validates that:
        - User can be retrieved by user_id
        - Returned user matches created user
        """
        retrieved_user = crud.get_user_by_id(test_db, user_id=test_user.user_id)

        assert retrieved_user is not None
        assert retrieved_user.user_id == test_user.user_id
        assert retrieved_user.email == test_user.email
        assert retrieved_user.user_name == test_user.user_name

    def test_get_user_by_email(self, test_db, test_user):
        """
        Test retrieving user by email.

        Validates that:
        - User can be retrieved by email address
        - Returned user matches created user
        """
        retrieved_user = crud.get_user_by_email(test_db, user_email=test_user.email)

        assert retrieved_user is not None
        assert retrieved_user.email == test_user.email
        assert retrieved_user.user_id == test_user.user_id

    def test_get_user_by_username(self, test_db, test_user):
        """
        Test retrieving user by username.

        Validates that:
        - User can be retrieved by username
        - Returned user matches created user
        """
        retrieved_user = crud.get_user_by_username(test_db, username=test_user.user_name)

        assert retrieved_user is not None
        assert retrieved_user.user_name == test_user.user_name
        assert retrieved_user.user_id == test_user.user_id

    def test_get_nonexistent_user_returns_none(self, test_db):
        """
        Test retrieving non-existent user returns None.

        Validates that:
        - Returns None for non-existent user_id
        - Returns None for non-existent email
        - Returns None for non-existent username
        """
        assert crud.get_user_by_id(test_db, user_id=99999) is None
        assert crud.get_user_by_email(test_db, user_email="nonexistent@example.com") is None
        assert crud.get_user_by_username(test_db, username="nonexistentuser") is None

    def test_get_all_users(self, test_db, test_user, second_test_user):
        """
        Test retrieving all users.

        Validates that:
        - All users in database are returned
        - Returned list contains correct number of users
        """
        all_users = crud.get_users(test_db)

        assert len(all_users) == 2
        user_emails = [user.email for user in all_users]
        assert test_user.email in user_emails
        assert second_test_user.email in user_emails


class TestUserAuthentication:
    """Test suite for user authentication logic"""

    def test_authenticate_user_with_email_success(self, test_db, test_user):
        """
        Test successful authentication with email.

        Validates that:
        - User can authenticate with email and correct password
        - Returns user object on success
        """
        authenticated_user = crud.authenticate_user(
            test_db,
            username=test_user.email,
            password=test_user.plain_password
        )

        assert authenticated_user is not False
        assert authenticated_user.email == test_user.email
        assert authenticated_user.user_id == test_user.user_id

    def test_authenticate_user_with_username_success(self, test_db, test_user):
        """
        Test successful authentication with username.

        Validates that:
        - User can authenticate with username and correct password
        - Returns user object on success
        """
        authenticated_user = crud.authenticate_user(
            test_db,
            username=test_user.user_name,
            password=test_user.plain_password
        )

        assert authenticated_user is not False
        assert authenticated_user.user_name == test_user.user_name

    def test_authenticate_user_wrong_password(self, test_db, test_user):
        """
        Test authentication fails with wrong password.

        Validates that:
        - Returns False when password is incorrect
        - User exists but password doesn't match
        """
        authenticated_user = crud.authenticate_user(
            test_db,
            username=test_user.email,
            password="wrongpassword"
        )

        assert authenticated_user is False

    def test_authenticate_nonexistent_user(self, test_db):
        """
        Test authentication fails with non-existent user.

        Validates that:
        - Returns False when user doesn't exist
        - Handles both email and username
        """
        result = crud.authenticate_user(
            test_db,
            username="nonexistent@example.com",
            password="anypassword"
        )

        assert result is False


class TestPasswordSecurity:
    """Test suite for password security functions"""

    def test_password_hash_is_unique(self, test_db):
        """
        Test that hashing same password twice produces different hashes.

        Validates that:
        - Salt is used in hashing
        - Same password produces different hashes
        - Both hashes are valid
        """
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different due to unique salt
        assert hash1 != hash2

        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

    def test_password_hash_format(self, test_db):
        """
        Test that password hash follows bcrypt format.

        Validates that:
        - Hash starts with $2b$ (bcrypt identifier)
        - Hash has appropriate length
        """
        password = "securepassword"
        hashed = get_password_hash(password)

        assert hashed.startswith("$2b$")
        assert len(hashed) >= 60  # bcrypt hashes are typically 60 characters

    def test_verify_password_rejects_invalid(self, test_db):
        """
        Test that password verification correctly rejects wrong passwords.

        Validates that:
        - Similar passwords are rejected
        - Empty passwords are rejected
        - Case-sensitive verification
        """
        password = "CorrectPassword"
        hashed = get_password_hash(password)

        # These should all fail
        assert not verify_password("WrongPassword", hashed)
        assert not verify_password("correctpassword", hashed)  # case different
        assert not verify_password("CorrectPasswor", hashed)  # missing char
        assert not verify_password("", hashed)


# Run tests with: pytest tests/test_services/test_user_service.py -v
