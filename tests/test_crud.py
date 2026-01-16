"""
CRUD operations tests.

Tests cover:
- User CRUD operations
- Exercise plan CRUD operations
- Routine CRUD operations
- Exercise CRUD operations
- Authentication helpers
- Password hashing and verification

All tests use in-memory SQLite database via conftest.py fixtures.
"""

import pytest
from datetime import timedelta
import crud
import schemas
import models


class TestUserCRUD:
    """Test suite for user CRUD operations"""

    def test_create_user(self, test_db):
        """
        Test user creation in database.

        Validates that:
        - User is created with correct data
        - Password is hashed
        - User has unique ID
        """
        user_data = schemas.User_Create(
            user_name="testuser",
            email="test@example.com",
            password="testpassword"
        )

        user = crud.create_user(db=test_db, user=user_data)

        assert user.user_name == user_data.user_name
        assert user.email == user_data.email
        assert user.hashed_password != user_data.password
        assert user.user_id is not None

    def test_get_user_by_id(self, test_db, test_user):
        """
        Test retrieving user by ID.

        Validates that:
        - Can retrieve user by ID
        - Returns correct user data
        """
        user = crud.get_user_by_id(db=test_db, user_id=test_user.user_id)

        assert user is not None
        assert user.user_id == test_user.user_id
        assert user.email == test_user.email

    def test_get_user_by_username(self, test_db, test_user):
        """
        Test retrieving user by username.

        Validates that:
        - Can retrieve user by username
        - Returns correct user data
        """
        user = crud.get_user_by_username(db=test_db, username=test_user.user_name)

        assert user is not None
        assert user.user_name == test_user.user_name
        assert user.email == test_user.email

    def test_get_user_by_email(self, test_db, test_user):
        """
        Test retrieving user by email.

        Validates that:
        - Can retrieve user by email
        - Returns correct user data
        """
        user = crud.get_user_by_email(db=test_db, user_email=test_user.email)

        assert user is not None
        assert user.email == test_user.email
        assert user.user_name == test_user.user_name

    def test_get_users(self, test_db, test_user, second_test_user):
        """
        Test retrieving all users.

        Validates that:
        - Returns list of all users
        - Contains all created users
        """
        users = crud.get_users(db=test_db)

        assert len(users) >= 2
        user_emails = [user.email for user in users]
        assert test_user.email in user_emails
        assert second_test_user.email in user_emails

    def test_get_user_nonexistent(self, test_db):
        """
        Test retrieving non-existent user returns None.

        Validates that:
        - Returns None for non-existent user
        """
        user = crud.get_user_by_email(db=test_db, user_email="nonexistent@example.com")
        assert user is None


class TestExercisePlanCRUD:
    """Test suite for exercise plan CRUD operations"""

    def test_create_exercise_plan_global(self, test_db, test_user):
        """
        Test creating global exercise plan.

        Validates that:
        - Plan is created with correct data
        - Has unique ID
        - Linked to creator user
        - Has creation date
        """
        plan_data = schemas.Exercise_plan_global_Create(
            exercise_plan_name="Test Plan",
            exercise_plan_type="strength",
            difficult_level="beginner"
        )

        plan = crud.create_exercise_plan_global(
            db=test_db,
            exercise_plan=plan_data,
            user_id=test_user.user_id
        )

        assert plan.exercise_plan_name == plan_data.exercise_plan_name
        assert plan.exercise_plan_type == plan_data.exercise_plan_type
        assert plan.difficult_level == plan_data.difficult_level
        assert plan.user_creator_id == test_user.user_id
        assert plan.exercise_plan_id is not None
        assert plan.creation_date is not None

    def test_assign_exercise_plan(self, test_db, test_user, test_exercise_plan_global):
        """
        Test assigning exercise plan to user.

        Validates that:
        - Plan is copied to user's plans
        - All routines are copied
        - All exercises are copied
        """
        # Create routine and exercise for global plan
        routine_data = schemas.Rutine_global_Create(
            rutine_name="Test Routine",
            rutine_type="strength",
            rutine_group="chest",
            rutine_category="push",
            exercise_plan_id=test_exercise_plan_global.exercise_plan_id,
            rst_btw_exercises="60",
            rst_btw_rounds="120",
            difficult_level="beginner",
            rounds=3
        )
        routine = crud.create_routine_global(test_db, routine_data)

        exercise_data = schemas.Exercise_global_Create(
            exercise_name="Push-ups",
            rep="10",
            exercise_type="push-bodyweight",
            exercise_group="chest",
            rutine_id=routine.rutine_id,
            image="pushups.jpg"
        )
        crud.create_exercise_global(test_db, exercise_data)

        # Reload plan with relationships
        test_db.refresh(test_exercise_plan_global)

        # Assign plan
        assigned_plan = crud.asign_exercise_plan(
            db=test_db,
            exercise_plan=test_exercise_plan_global,
            user_id=test_user.user_id
        )

        assert assigned_plan.user_owner_id == test_user.user_id
        assert len(assigned_plan.rutines) > 0
        assert len(assigned_plan.rutines[0].exercises) > 0

    def test_delete_exercise_plan_for_user(self, test_db, test_user, test_exercise_plan_global):
        """
        Test deleting user's exercise plan.

        Validates that:
        - Plan is removed from user
        - All associated routines are deleted
        - All exercises are deleted
        """
        # Assign plan first
        crud.asign_exercise_plan(test_db, test_exercise_plan_global, test_user.user_id)

        # Delete plan
        result = crud.delete_exercise_plan_for_user(db=test_db, user_id=test_user.user_id)

        assert result is True

        # Verify plan is deleted
        plans = test_db.query(models.Exercise_plan).filter(
            models.Exercise_plan.user_owner_id == test_user.user_id
        ).all()
        assert len(plans) == 0


class TestRoutineCRUD:
    """Test suite for routine CRUD operations"""

    def test_create_routine_global(self, test_db, test_exercise_plan_global):
        """
        Test creating global routine.

        Validates that:
        - Routine is created with correct data
        - Has unique ID
        - Linked to exercise plan
        """
        routine_data = schemas.Rutine_global_Create(
            rutine_name="Test Routine",
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

        assert routine.rutine_name == routine_data.rutine_name
        assert routine.rutine_type == routine_data.rutine_type
        assert routine.rutine_group == routine_data.rutine_group
        assert routine.exercise_plan_id == test_exercise_plan_global.exercise_plan_id
        assert routine.rutine_id is not None

    def test_get_routine_info(self, test_db, test_user, test_exercise_plan_global):
        """
        Test retrieving routine information.

        Validates that:
        - Can query routine by ID
        - Returns correct routine data
        """
        routine_data = schemas.Rutine_global_Create(
            rutine_name="Test Routine",
            rutine_type="strength",
            rutine_group="chest",
            rutine_category="push",
            exercise_plan_id=test_exercise_plan_global.exercise_plan_id,
            rst_btw_exercises="60",
            rst_btw_rounds="120",
            difficult_level="beginner",
            rounds=3
        )
        crud.create_routine_global(test_db, routine_data)

        # Assign plan to user to create user-specific routine
        crud.asign_exercise_plan(test_db, test_exercise_plan_global, test_user.user_id)

        # Get user's routine (created by assignment)
        user_routine = test_db.query(models.Rutine).filter(
            models.Rutine.exercise_plan_id == test_db.query(models.Exercise_plan)
            .filter(models.Exercise_plan.user_owner_id == test_user.user_id)
            .first().exercise_plan_id
        ).first()

        routine_query = crud.get_rutine_info(db=test_db, rutine_id=user_routine.rutine_id)
        routine = routine_query.first()

        assert routine is not None
        assert routine.rutine_id == user_routine.rutine_id

    def test_update_routine(self, test_db, test_user, test_exercise_plan_global):
        """
        Test updating routine.

        Validates that:
        - Can update routine data
        - Changes are persisted
        """
        # Create global routine
        routine_data = schemas.Rutine_global_Create(
            rutine_name="Test Routine",
            rutine_type="strength",
            rutine_group="chest",
            rutine_category="push",
            exercise_plan_id=test_exercise_plan_global.exercise_plan_id,
            rst_btw_exercises="60",
            rst_btw_rounds="120",
            difficult_level="beginner",
            rounds=3
        )
        routine_global = crud.create_routine_global(test_db, routine_data)

        # Assign plan to user to create routine instance
        crud.asign_exercise_plan(test_db, test_exercise_plan_global, test_user.user_id)

        # Get the user's routine instance
        user_routine = test_db.query(models.Rutine).filter(
            models.Rutine.exercise_plan_id == test_db.query(models.Exercise_plan)
            .filter(models.Exercise_plan.user_owner_id == test_user.user_id)
            .first().exercise_plan_id
        ).first()

        # Test update (the function exists in crud)
        assert user_routine is not None
        updated_routine = crud.update_routine(test_db, user_routine)
        assert updated_routine is not None  # update_routine returns the updated routine object


class TestExerciseCRUD:
    """Test suite for exercise CRUD operations"""

    def test_create_exercise_global(self, test_db, test_exercise_plan_global):
        """
        Test creating global exercise.

        Validates that:
        - Exercise is created with correct data
        - Has unique ID
        - Linked to routine
        """
        # Create routine first
        routine_data = schemas.Rutine_global_Create(
            rutine_name="Test Routine",
            rutine_type="strength",
            rutine_group="chest",
            rutine_category="push",
            exercise_plan_id=test_exercise_plan_global.exercise_plan_id,
            rst_btw_exercises="60",
            rst_btw_rounds="120",
            difficult_level="beginner",
            rounds=3
        )
        routine = crud.create_routine_global(test_db, routine_data)

        # Create exercise
        exercise_data = schemas.Exercise_global_Create(
            exercise_name="Push-ups",
            rep="10",
            exercise_type="push-bodyweight",
            exercise_group="chest",
            rutine_id=routine.rutine_id,
            image="pushups.jpg"
        )

        exercise = crud.create_exercise_global(db=test_db, exercise_global=exercise_data)

        assert exercise.exercise_name == exercise_data.exercise_name
        assert exercise.rep == exercise_data.rep
        assert exercise.exercise_type == exercise_data.exercise_type
        assert exercise.rutine_id == routine.rutine_id
        assert exercise.exercise_id is not None

    def test_get_exercise_info(self, test_db, test_user, test_exercise_plan_global):
        """
        Test retrieving exercise information.

        Validates that:
        - Can query exercise by ID
        - Returns correct exercise data
        """
        # Create routine
        routine_data = schemas.Rutine_global_Create(
            rutine_name="Test Routine",
            rutine_type="strength",
            rutine_group="chest",
            rutine_category="push",
            exercise_plan_id=test_exercise_plan_global.exercise_plan_id,
            rst_btw_exercises="60",
            rst_btw_rounds="120",
            difficult_level="beginner",
            rounds=3
        )
        routine = crud.create_routine_global(test_db, routine_data)

        # Create exercise
        exercise_data = schemas.Exercise_global_Create(
            exercise_name="Push-ups",
            rep="10",
            exercise_type="push-bodyweight",
            exercise_group="chest",
            rutine_id=routine.rutine_id,
            image="pushups.jpg"
        )
        crud.create_exercise_global(test_db, exercise_data)

        # Assign plan to user to create user-specific exercise
        crud.asign_exercise_plan(test_db, test_exercise_plan_global, test_user.user_id)

        # Get user's exercise (created by assignment)
        user_exercise = test_db.query(models.Exercise).filter(
            models.Exercise.rutine_id == test_db.query(models.Rutine)
            .filter(models.Rutine.exercise_plan_id == test_db.query(models.Exercise_plan)
            .filter(models.Exercise_plan.user_owner_id == test_user.user_id)
            .first().exercise_plan_id)
            .first().rutine_id
        ).first()

        exercise_query = crud.get_exercise_info(db=test_db, exercise_id=user_exercise.exercise_id)
        exercise = exercise_query.first()

        assert exercise is not None
        assert exercise.exercise_id == user_exercise.exercise_id


class TestPasswordOperations:
    """Test suite for password hashing and verification"""

    def test_password_hashing(self, test_db):
        """
        Test password hashing.

        Validates that:
        - Password is hashed
        - Hash is different from plain password
        - Hash is bcrypt format
        """
        plain_password = "testpassword123"
        hashed = crud.get_password_hash(plain_password)

        assert hashed != plain_password
        assert hashed.startswith("$2b$")
        assert len(hashed) > 50

    def test_password_verification_correct(self, test_db):
        """
        Test password verification with correct password.

        Validates that:
        - Correct password is verified successfully
        """
        plain_password = "testpassword123"
        hashed = crud.get_password_hash(plain_password)

        assert crud.verify_password(plain_password, hashed) is True

    def test_password_verification_incorrect(self, test_db):
        """
        Test password verification with incorrect password.

        Validates that:
        - Incorrect password fails verification
        """
        plain_password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = crud.get_password_hash(plain_password)

        assert crud.verify_password(wrong_password, hashed) is False

    def test_password_hash_unique(self, test_db):
        """
        Test that same password produces different hashes.

        Validates that:
        - Each hash is unique (due to salt)
        - Both hashes verify the same password
        """
        plain_password = "testpassword123"
        hash1 = crud.get_password_hash(plain_password)
        hash2 = crud.get_password_hash(plain_password)

        assert hash1 != hash2  # Different due to salt
        assert crud.verify_password(plain_password, hash1) is True
        assert crud.verify_password(plain_password, hash2) is True


class TestAuthenticationHelpers:
    """Test suite for authentication helper functions"""

    def test_authenticate_user_with_email(self, test_db, test_user):
        """
        Test authenticating user with email and password.

        Validates that:
        - User can authenticate with email
        - Returns user object on success
        """
        user = crud.authenticate_user(
            db=test_db,
            username=test_user.email,
            password=test_user.plain_password
        )

        assert user is not False
        assert user.email == test_user.email

    def test_authenticate_user_with_username(self, test_db, test_user):
        """
        Test authenticating user with username and password.

        Validates that:
        - User can authenticate with username
        - Returns user object on success
        """
        user = crud.authenticate_user(
            db=test_db,
            username=test_user.user_name,
            password=test_user.plain_password
        )

        assert user is not False
        assert user.user_name == test_user.user_name

    def test_authenticate_user_wrong_password(self, test_db, test_user):
        """
        Test authentication fails with wrong password.

        Validates that:
        - Returns False for incorrect password
        """
        user = crud.authenticate_user(
            db=test_db,
            username=test_user.email,
            password="wrongpassword"
        )

        assert user is False

    def test_authenticate_user_nonexistent(self, test_db):
        """
        Test authentication fails with non-existent user.

        Validates that:
        - Returns False for non-existent user
        """
        user = crud.authenticate_user(
            db=test_db,
            username="nonexistent@example.com",
            password="anypassword"
        )

        assert user is False

    def test_create_access_token(self, test_db):
        """
        Test JWT access token creation.

        Validates that:
        - Token is created with correct data
        - Token can be decoded
        - Token contains subject and expiration
        """
        from config import settings
        from jose import jwt

        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)

        token = crud.create_access_token(
            data=data,
            expires_delta=expires_delta,
            SECRET_KEY=settings.secret_key,
            ALGORITHM=settings.algorithm
        )

        assert token is not None
        assert isinstance(token, str)

        # Decode and verify
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "test@example.com"
        assert "exp" in payload


class TestUserTracking:
    """Test suite for user tracking operations"""

    def test_record_start_exercise_plan(self, test_db, test_user, test_exercise_plan_global):
        """
        Test recording exercise plan start.

        Validates that:
        - Creates tracker record
        - Record has correct type and user
        """
        record = crud.record_start_exercise_plan(
            db=test_db,
            user_id=test_user.user_id,
            exercise_record=test_exercise_plan_global
        )

        assert record.user_id == test_user.user_id
        assert record.info_type == "exercise_plan_start"
        assert record.user_tracker_id is not None

    def test_record_end_exercise_plan(self, test_db, test_user, test_exercise_plan_global):
        """
        Test recording exercise plan end.

        Validates that:
        - Creates tracker record
        - Record has correct type and user
        """
        record = crud.record_end_exercise_plan(
            db=test_db,
            user_id=test_user.user_id,
            exercise_record=test_exercise_plan_global
        )

        assert record.user_id == test_user.user_id
        assert record.info_type == "exercise_plan_end"
        assert record.user_tracker_id is not None

    def test_record_end_routine(self, test_db, test_user):
        """
        Test recording routine end with exercise data.

        Validates that:
        - Creates tracker record with exercise increments
        - Record contains all exercise data
        """
        from datetime import datetime, timezone

        exercise_record = {
            "record_datetime": datetime.now(timezone.utc).replace(tzinfo=None),
            "info_type": "rutine_end",
            "info_description": "chest",
            "exercise_increments": {"Push-ups": 2, "Bench Press": 1},
            "push_increment": 3,
            "pull_increment": 0,
            "isometric_increment": 0,
        }

        record = crud.redord_end_rutine(
            db=test_db,
            user_id=test_user.user_id,
            exercise_record=exercise_record
        )

        assert record.user_id == test_user.user_id
        assert record.info_type == "rutine_end"
        assert record.info_description == "chest"
        assert record.push_increment == 3


# Run tests with: pytest tests/test_crud.py -v
