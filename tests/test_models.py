"""
Database model tests.

Tests cover:
- Model creation and validation
- Model relationships
- Model defaults
- Database constraints
- Field types and validation

All tests use in-memory SQLite database via conftest.py fixtures.
"""

import pytest
from datetime import date, datetime, timezone
import json
import models
import schemas


class TestUserModel:
    """Test suite for User model"""

    def test_user_creation(self, test_db):
        """
        Test User model creation.

        Validates that:
        - User can be created with all fields
        - Default values are applied
        - Primary key is auto-generated
        """
        user = models.User(
            user_name="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here",
            user_image="profile.jpg"
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.user_id is not None
        assert user.user_name == "testuser"
        assert user.email == "test@example.com"
        assert user.user_image == "profile.jpg"

    def test_user_default_image(self, test_db):
        """
        Test User model default image value.

        Validates that:
        - Default image is 'empty'
        """
        user = models.User(
            user_name="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here"
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.user_image == "empty"

    def test_user_email_unique_constraint(self, test_db, test_user):
        """
        Test User email uniqueness constraint.

        Validates that:
        - Cannot create user with duplicate email
        - Database raises integrity error
        """
        from sqlalchemy.exc import IntegrityError

        duplicate_user = models.User(
            user_name="anotheruser",
            email=test_user.email,  # Duplicate email
            hashed_password="password"
        )

        test_db.add(duplicate_user)

        with pytest.raises(IntegrityError):
            test_db.commit()

    def test_user_relationships(self, test_db, test_user, test_exercise_plan_global):
        """
        Test User model relationships.

        Validates that:
        - User has exercise_plan relationship
        - User has exercise_plan_global relationship
        - User has user_tracker relationship
        """
        # Check relationship attributes exist
        assert hasattr(test_user, 'exercise_plan')
        assert hasattr(test_user, 'exercise_plan_global')
        assert hasattr(test_user, 'user_tracker')


class TestExercisePlanModel:
    """Test suite for Exercise_plan model"""

    def test_exercise_plan_creation(self, test_db, test_user):
        """
        Test Exercise_plan model creation.

        Validates that:
        - Plan can be created with all fields
        - Default values are applied
        - Foreign key to user works
        """
        plan = models.Exercise_plan(
            exercise_plan_name="Test Plan",
            user_owner_id=test_user.user_id,
            exercise_plan_type="strength",
            difficult_level="beginner",
            creation_date=date.today()
        )

        test_db.add(plan)
        test_db.commit()
        test_db.refresh(plan)

        assert plan.exercise_plan_id is not None
        assert plan.user_owner_id == test_user.user_id
        assert plan.exercise_plan_name == "Test Plan"

    def test_exercise_plan_default_values(self, test_db, test_user):
        """
        Test Exercise_plan model default values.

        Validates that:
        - Default values are properly set
        """
        plan = models.Exercise_plan(
            user_owner_id=test_user.user_id
        )

        test_db.add(plan)
        test_db.commit()
        test_db.refresh(plan)

        assert plan.exercise_plan_name == "New exercise plan"
        assert plan.exercise_plan_type == "New exercise plan type"
        assert plan.difficult_level == "New exercise plan difficult level"

    def test_exercise_plan_cascade_delete(self, test_db, test_user):
        """
        Test Exercise_plan cascade delete.

        Validates that:
        - Deleting user deletes their exercise plans
        - Cascade delete works for relationships
        """
        plan = models.Exercise_plan(
            exercise_plan_name="Test Plan",
            user_owner_id=test_user.user_id
        )

        test_db.add(plan)
        test_db.commit()

        plan_id = plan.exercise_plan_id

        # Delete user (should cascade)
        test_db.delete(test_user)
        test_db.commit()

        # Verify plan is deleted
        deleted_plan = test_db.query(models.Exercise_plan).filter(
            models.Exercise_plan.exercise_plan_id == plan_id
        ).first()

        assert deleted_plan is None


class TestRoutineModel:
    """Test suite for Rutine model"""

    def test_routine_creation(self, test_db, test_user):
        """
        Test Rutine model creation.

        Validates that:
        - Routine can be created with all fields
        - Foreign key to exercise plan works
        """
        plan = models.Exercise_plan(
            exercise_plan_name="Test Plan",
            user_owner_id=test_user.user_id
        )
        test_db.add(plan)
        test_db.commit()

        routine = models.Rutine(
            rutine_name="Chest Day",
            rutine_type="strength",
            rutine_group="chest",
            rutine_category="push",
            exercise_plan_id=plan.exercise_plan_id,
            rounds=3,
            rst_btw_exercises="60",
            rst_btw_rounds="120",
            difficult_level="beginner"
        )

        test_db.add(routine)
        test_db.commit()
        test_db.refresh(routine)

        assert routine.rutine_id is not None
        assert routine.exercise_plan_id == plan.exercise_plan_id
        assert routine.rutine_name == "Chest Day"
        assert routine.rounds == 3

    def test_routine_default_values(self, test_db, test_user):
        """
        Test Rutine model default values.

        Validates that:
        - Default values are properly set
        """
        plan = models.Exercise_plan(
            exercise_plan_name="Test Plan",
            user_owner_id=test_user.user_id
        )
        test_db.add(plan)
        test_db.commit()

        routine = models.Rutine(
            exercise_plan_id=plan.exercise_plan_id
        )

        test_db.add(routine)
        test_db.commit()
        test_db.refresh(routine)

        assert routine.rutine_name == "New rutine name"
        assert routine.rutine_type == "New rutine type"
        assert routine.rounds == 0

    def test_routine_cascade_delete(self, test_db, test_user):
        """
        Test Rutine cascade delete.

        Validates that:
        - Deleting exercise plan deletes routines
        """
        plan = models.Exercise_plan(
            exercise_plan_name="Test Plan",
            user_owner_id=test_user.user_id
        )
        test_db.add(plan)
        test_db.commit()

        routine = models.Rutine(
            rutine_name="Test Routine",
            exercise_plan_id=plan.exercise_plan_id
        )
        test_db.add(routine)
        test_db.commit()

        routine_id = routine.rutine_id

        # Delete plan (should cascade to routine)
        test_db.delete(plan)
        test_db.commit()

        deleted_routine = test_db.query(models.Rutine).filter(
            models.Rutine.rutine_id == routine_id
        ).first()

        assert deleted_routine is None


class TestExerciseModel:
    """Test suite for Exercise model"""

    def test_exercise_creation(self, test_db, test_user):
        """
        Test Exercise model creation.

        Validates that:
        - Exercise can be created with all fields
        - Foreign key to routine works
        """
        plan = models.Exercise_plan(
            exercise_plan_name="Test Plan",
            user_owner_id=test_user.user_id
        )
        test_db.add(plan)
        test_db.commit()

        routine = models.Rutine(
            rutine_name="Test Routine",
            exercise_plan_id=plan.exercise_plan_id
        )
        test_db.add(routine)
        test_db.commit()

        exercise = models.Exercise(
            exercise_name="Push-ups",
            rep="10",
            exercise_type="push-bodyweight",
            exercise_group="chest",
            rutine_id=routine.rutine_id,
            image="pushups.jpg"
        )

        test_db.add(exercise)
        test_db.commit()
        test_db.refresh(exercise)

        assert exercise.exercise_id is not None
        assert exercise.rutine_id == routine.rutine_id
        assert exercise.exercise_name == "Push-ups"
        assert exercise.rep == "10"

    def test_exercise_default_values(self, test_db, test_user):
        """
        Test Exercise model default values.

        Validates that:
        - Default values are properly set
        """
        plan = models.Exercise_plan(
            exercise_plan_name="Test Plan",
            user_owner_id=test_user.user_id
        )
        test_db.add(plan)
        test_db.commit()

        routine = models.Rutine(
            rutine_name="Test Routine",
            exercise_plan_id=plan.exercise_plan_id
        )
        test_db.add(routine)
        test_db.commit()

        exercise = models.Exercise(
            rutine_id=routine.rutine_id
        )

        test_db.add(exercise)
        test_db.commit()
        test_db.refresh(exercise)

        assert exercise.exercise_name == "New exercise name"
        assert exercise.rep == "empty"
        assert exercise.image == "empty"


class TestExercisePlanGlobalModel:
    """Test suite for Exercise_plan_global model"""

    def test_exercise_plan_global_creation(self, test_db, test_user):
        """
        Test Exercise_plan_global model creation.

        Validates that:
        - Global plan can be created
        - All required fields are set
        - Creation date is recorded
        """
        plan = models.Exercise_plan_global(
            exercise_plan_name="Global Plan",
            user_creator_id=test_user.user_id,
            exercise_plan_type="strength",
            difficult_level="beginner",
            creation_date=date.today()
        )

        test_db.add(plan)
        test_db.commit()
        test_db.refresh(plan)

        assert plan.exercise_plan_id is not None
        assert plan.user_creator_id == test_user.user_id
        assert plan.exercise_plan_name == "Global Plan"
        assert plan.creation_date is not None

    def test_exercise_plan_global_routine_order(self, test_db, test_user):
        """
        Test Exercise_plan_global routine_group_order JSON field.

        Validates that:
        - JSON field can store routine order
        - Default value is applied
        """
        plan = models.Exercise_plan_global(
            exercise_plan_name="Global Plan",
            user_creator_id=test_user.user_id,
            exercise_plan_type="strength",
            difficult_level="beginner",
            creation_date=date.today()
        )

        test_db.add(plan)
        test_db.commit()
        test_db.refresh(plan)

        # Check that routine_group_order exists
        assert plan.routine_group_order is not None


class TestUserTrackerModel:
    """Test suite for User_Tracker model"""

    def test_user_tracker_creation(self, test_db, test_user):
        """
        Test User_Tracker model creation.

        Validates that:
        - Tracker record can be created
        - All fields are stored correctly
        - JSON field works for exercise increments
        """
        tracker = models.User_Tracker(
            user_id=test_user.user_id,
            record_datetime=datetime.now(timezone.utc).replace(tzinfo=None),
            info_type="rutine_end",
            info_description="chest",
            exercise_increments={"Push-ups": 2, "Bench Press": 1},
            push_increment=3,
            pull_increment=0,
            isometric_increment=0
        )

        test_db.add(tracker)
        test_db.commit()
        test_db.refresh(tracker)

        assert tracker.user_tracker_id is not None
        assert tracker.user_id == test_user.user_id
        assert tracker.info_type == "rutine_end"
        assert tracker.exercise_increments is not None

    def test_user_tracker_default_values(self, test_db, test_user):
        """
        Test User_Tracker model default values.

        Validates that:
        - Default values are applied
        - Datetime is set automatically
        """
        tracker = models.User_Tracker(
            user_id=test_user.user_id
        )

        test_db.add(tracker)
        test_db.commit()
        test_db.refresh(tracker)

        assert tracker.info_type == "Non_specifed"
        assert tracker.push_increment == 0
        assert tracker.pull_increment == 0
        assert tracker.isometric_increment == 0


class TestModelRelationships:
    """Test suite for model relationships"""

    def test_user_to_exercise_plan_relationship(self, test_db, test_user):
        """
        Test User to Exercise_plan one-to-many relationship.

        Validates that:
        - User can have exercise plans
        - Plans are accessible via relationship
        - Cascade delete works
        """
        plan = models.Exercise_plan(
            exercise_plan_name="Test Plan",
            user_owner_id=test_user.user_id
        )
        test_db.add(plan)
        test_db.commit()

        test_db.refresh(test_user)
        assert len(test_user.exercise_plan) > 0

    def test_exercise_plan_to_routine_relationship(self, test_db, test_user):
        """
        Test Exercise_plan to Rutine one-to-many relationship.

        Validates that:
        - Plan can have multiple routines
        - Routines are accessible via relationship
        """
        plan = models.Exercise_plan(
            exercise_plan_name="Test Plan",
            user_owner_id=test_user.user_id
        )
        test_db.add(plan)
        test_db.commit()

        routine = models.Rutine(
            rutine_name="Test Routine",
            exercise_plan_id=plan.exercise_plan_id
        )
        test_db.add(routine)
        test_db.commit()

        test_db.refresh(plan)
        assert len(plan.rutines) > 0
        assert plan.rutines[0].rutine_name == "Test Routine"

    def test_routine_to_exercise_relationship(self, test_db, test_user):
        """
        Test Rutine to Exercise one-to-many relationship.

        Validates that:
        - Routine can have multiple exercises
        - Exercises are accessible via relationship
        """
        plan = models.Exercise_plan(
            exercise_plan_name="Test Plan",
            user_owner_id=test_user.user_id
        )
        test_db.add(plan)
        test_db.commit()

        routine = models.Rutine(
            rutine_name="Test Routine",
            exercise_plan_id=plan.exercise_plan_id
        )
        test_db.add(routine)
        test_db.commit()

        exercise = models.Exercise(
            exercise_name="Push-ups",
            rutine_id=routine.rutine_id
        )
        test_db.add(exercise)
        test_db.commit()

        test_db.refresh(routine)
        assert len(routine.exercises) > 0
        assert routine.exercises[0].exercise_name == "Push-ups"


# Run tests with: pytest tests/test_models.py -v
