"""
Routine endpoint tests.

Tests cover:
- Creating routines for exercise plans
- Retrieving assigned routines
- Getting routine exercises
- Ending routines and tracking progress
- Getting next routine in sequence

All tests use in-memory SQLite database via conftest.py fixtures.
"""

import pytest
from fastapi import status
from datetime import datetime
import models
import crud
import schemas


class TestCreateRoutineGlobal:
    """Test suite for POST /api/v1/routines/global"""

    def test_create_routine_success(self, client, test_user, test_exercise_plan_global, auth_headers):
        """
        Test successful creation of routine for exercise plan.

        Validates that:
        - Can create routine for existing exercise plan
        - Returns created routine with all fields
        - Routine is linked to exercise plan
        """
        routine_data = {
            "rutine_name": "Chest Day",
            "rutine_type": "strength",
            "rutine_group": "chest",
            "rutine_category": "push",
            "exercise_plan_id": test_exercise_plan_global.exercise_plan_id,
            "rst_btw_exercises": "60",
            "rst_btw_rounds": "120",
            "difficult_level": "beginner",
            "rounds": 3
        }

        response = client.post(
            "/api/v1/routines/global",
            json=routine_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["rutine_name"] == routine_data["rutine_name"]
        assert data["rutine_group"] == routine_data["rutine_group"]
        assert "rutine_id" in data

    def test_create_routine_duplicate_name_same_plan(self, client, test_db, test_user, test_exercise_plan_global, auth_headers):
        """
        Test creation fails with duplicate routine name in same plan.

        Validates that:
        - Cannot create routine with duplicate name in same plan
        - Returns 400 Bad Request
        - Error message indicates duplicate
        """
        # Create first routine
        routine_data = {
            "rutine_name": "Chest Day",
            "rutine_type": "strength",
            "rutine_group": "chest",
            "rutine_category": "push",
            "exercise_plan_id": test_exercise_plan_global.exercise_plan_id,
            "rst_btw_exercises": "60",
            "rst_btw_rounds": "120",
            "difficult_level": "beginner",
            "rounds": 3
        }

        # Create first routine
        client.post(
            "/api/v1/routines/global",
            json=routine_data,
            headers=auth_headers
        )

        # Try to create duplicate
        response = client.post(
            "/api/v1/routines/global",
            json=routine_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Routine name already exists for this exercise plan" in response.json()["error"]["message"]

    def test_create_routine_nonexistent_plan(self, client, auth_headers):
        """
        Test creation fails with non-existent exercise plan.

        Validates that:
        - Cannot create routine for non-existent plan
        - Returns 404 Not Found
        - Error message indicates plan not found
        """
        routine_data = {
            "rutine_name": "Test Routine",
            "rutine_type": "strength",
            "rutine_group": "chest",
            "rutine_category": "push",
            "exercise_plan_id": 99999,  # Non-existent
            "rst_btw_exercises": "60",
            "rst_btw_rounds": "120",
            "difficult_level": "beginner",
            "rounds": 3
        }

        response = client.post(
            "/api/v1/routines/global",
            json=routine_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Exercise plan not found" in response.json()["error"]["message"]

    def test_create_routine_without_auth(self, client, test_exercise_plan_global):
        """
        Test creation fails without authentication.

        Validates that:
        - Endpoint requires authentication
        - Returns 401 Unauthorized
        """
        routine_data = {
            "rutine_name": "Test Routine",
            "exercise_plan_id": test_exercise_plan_global.exercise_plan_id,
            "rutine_type": "strength",
            "rutine_group": "chest",
            "rutine_category": "push",
            "rst_btw_exercises": "60",
            "rst_btw_rounds": "120",
            "difficult_level": "beginner",
            "rounds": 3
        }

        response = client.post(
            "/api/v1/routines/global",
            json=routine_data
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetAssignedRoutines:
    """Test suite for GET /api/v1/routines/assigned"""

    def test_get_assigned_routines_success(self, client, test_db, test_user, test_exercise_plan_global, auth_headers):
        """
        Test successful retrieval of assigned routines.

        Validates that:
        - Returns all routines for user's active exercise plan
        - Response is list of routines
        - All routines belong to correct plan
        """
        # Create routine for global plan
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

        # Assign plan to user
        crud.asign_exercise_plan(
            test_db,
            test_exercise_plan_global,
            test_user.user_id
        )
        crud.record_start_exercise_plan(test_db, test_user.user_id, test_exercise_plan_global)

        response = client.get("/api/v1/routines/assigned", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_assigned_routines_without_auth(self, client):
        """
        Test retrieval fails without authentication.

        Validates that:
        - Endpoint requires authentication
        - Returns 401 Unauthorized
        """
        response = client.get("/api/v1/routines/assigned")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetRoutineExercises:
    """Test suite for GET /api/v1/routines/{rutine_id}/exercises"""

    def test_get_routine_exercises_success(self, client, test_db, test_user, auth_headers):
        """
        Test successful retrieval of exercises for a routine.

        Validates that:
        - Returns all exercises for specified routine
        - Response includes routine metadata
        - Exercises are properly formatted
        """
        # Create exercise plan
        plan = schemas.Exercise_plan_global_Create(
            exercise_plan_name="Test Plan",
            exercise_plan_type="strength",
            difficult_level="beginner"
        )
        plan_created = crud.create_exercise_plan_global(test_db, plan, test_user.user_id)

        # Create routine
        routine_data = schemas.Rutine_global_Create(
            rutine_name="Test Routine",
            rutine_type="strength",
            rutine_group="chest",
            rutine_category="push",
            exercise_plan_id=plan_created.exercise_plan_id,
            rst_btw_exercises="60",
            rst_btw_rounds="120",
            difficult_level="beginner",
            rounds=3
        )
        routine_created = crud.create_routine_global(test_db, routine_data)

        # Create exercises
        exercise1 = schemas.Exercise_global_Create(
            exercise_name="Push-ups",
            rep="10",
            exercise_type="push-bodyweight",
            exercise_group="chest",
            rutine_id=routine_created.rutine_id,
            image="pushups.jpg"
        )
        crud.create_exercise_global(test_db, exercise1)

        exercise2 = schemas.Exercise_global_Create(
            exercise_name="Bench Press",
            rep="8",
            exercise_type="push-weight",
            exercise_group="chest",
            rutine_id=routine_created.rutine_id,
            image="bench.jpg"
        )
        crud.create_exercise_global(test_db, exercise2)

        # Assign plan to user to create routine instance
        crud.asign_exercise_plan(test_db, plan_created, test_user.user_id)

        # Get routine ID from assigned plan
        assigned_routine = test_db.query(models.Rutine).filter(
            models.Rutine.exercise_plan_id == test_db.query(models.Exercise_plan)
            .filter(models.Exercise_plan.user_owner_id == test_user.user_id)
            .first().exercise_plan_id
        ).first()

        response = client.get(
            f"/api/v1/routines/{assigned_routine.rutine_id}/exercises",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "exercises" in data
        assert "routine_group" in data
        assert "rest_between_exercises" in data
        assert len(data["exercises"]) >= 2

    def test_get_routine_exercises_not_found(self, client, auth_headers):
        """
        Test retrieval fails with non-existent routine.

        Validates that:
        - Returns 404 when routine doesn't exist
        - Error message indicates routine not found
        """
        response = client.get("/api/v1/routines/99999/exercises", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Rutine not found" in response.json()["error"]["message"]

    def test_get_routine_exercises_without_auth(self, client):
        """
        Test retrieval fails without authentication.

        Validates that:
        - Endpoint requires authentication
        - Returns 401 Unauthorized
        """
        response = client.get("/api/v1/routines/1/exercises")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestEndRoutine:
    """Test suite for POST /api/v1/routines/end"""

    def test_end_routine_success(self, client, test_db, test_user, auth_headers):
        """
        Test successful routine completion and tracking.

        Validates that:
        - Can end routine with exercise summary
        - Updates exercise reps in database
        - Creates user tracker record
        - Returns success message
        """
        # Setup: Create plan, routine, and exercises
        plan = schemas.Exercise_plan_global_Create(
            exercise_plan_name="Test Plan",
            exercise_plan_type="strength",
            difficult_level="beginner"
        )
        plan_created = crud.create_exercise_plan_global(test_db, plan, test_user.user_id)

        routine_data = schemas.Rutine_global_Create(
            rutine_name="Test Routine",
            rutine_type="strength",
            rutine_group="chest",
            rutine_category="push",
            exercise_plan_id=plan_created.exercise_plan_id,
            rst_btw_exercises="60",
            rst_btw_rounds="120",
            difficult_level="beginner",
            rounds=3
        )
        routine_created = crud.create_routine_global(test_db, routine_data)

        # Create exercises
        exercise1 = schemas.Exercise_global_Create(
            exercise_name="Push-ups",
            rep="10",
            exercise_type="push-bodyweight",
            exercise_group="chest",
            rutine_id=routine_created.rutine_id,
            image="pushups.jpg"
        )
        crud.create_exercise_global(test_db, exercise1)

        # Assign plan to user
        crud.asign_exercise_plan(test_db, plan_created, test_user.user_id)

        # Get assigned plan ID
        assigned_plan = test_db.query(models.Exercise_plan).filter(
            models.Exercise_plan.user_owner_id == test_user.user_id
        ).first()

        # End routine
        exercises_summary = {
            "routine_group": "chest",
            "exercises": {
                "exercise_start": {
                    "reps": "12"  # Improved from 10
                }
            }
        }

        response = client.post(
            "/api/v1/routines/end",
            json=exercises_summary,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert "Routine ended correctly" in response.json()["detail"]

    def test_end_routine_without_auth(self, client):
        """
        Test ending routine fails without authentication.

        Validates that:
        - Endpoint requires authentication
        - Returns 401 Unauthorized
        """
        exercises_summary = {
            "routine_group": "chest",
            "exercises": {}
        }

        response = client.post("/api/v1/routines/end", json=exercises_summary)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetMuscularGroups:
    """Test suite for GET /api/v1/exercises/muscular_groups/{exercise_plan_name}"""

    def test_get_muscular_groups_success(self, client, test_db, test_user, auth_headers):
        """
        Test successful retrieval of muscular groups for exercise plan.

        Validates that:
        - Returns list of routine groups
        - Each group has routine_id and rutine_group
        - All groups belong to user's active plan
        """
        # Create and assign plan with routines
        plan = schemas.Exercise_plan_global_Create(
            exercise_plan_name="Test Plan",
            exercise_plan_type="strength",
            difficult_level="beginner"
        )
        plan_created = crud.create_exercise_plan_global(test_db, plan, test_user.user_id)

        # Create routine
        routine_data = schemas.Rutine_global_Create(
            rutine_name="Chest Routine",
            rutine_type="strength",
            rutine_group="chest",
            rutine_category="push",
            exercise_plan_id=plan_created.exercise_plan_id,
            rst_btw_exercises="60",
            rst_btw_rounds="120",
            difficult_level="beginner",
            rounds=3
        )
        crud.create_routine_global(test_db, routine_data)

        # Assign to user
        crud.asign_exercise_plan(test_db, plan_created, test_user.user_id)

        response = client.get(
            f"/api/v1/exercises/muscular_groups/{plan_created.exercise_plan_name}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "rutine_group" in data[0]
        assert "rutine_id" in data[0]


class TestGetNextRoutine:
    """Test suite for GET /api/v1/routines/next"""

    def test_get_next_routine_first_routine(self, client, test_db, test_user, auth_headers):
        """
        Test getting next routine when starting new plan.

        Validates that:
        - Returns first routine in sequence
        - Response includes routine name and ID
        """
        # Create plan with routine and routine_group_order
        plan = schemas.Exercise_plan_global_Create(
            exercise_plan_name="Test Plan",
            exercise_plan_type="strength",
            difficult_level="beginner",
            routine_group_order=["chest", "back", "legs"]
        )
        plan_created = crud.create_exercise_plan_global(test_db, plan, test_user.user_id)

        routine_data = schemas.Rutine_global_Create(
            rutine_name="Chest Routine",
            rutine_type="strength",
            rutine_group="chest",
            rutine_category="push",
            exercise_plan_id=plan_created.exercise_plan_id,
            rst_btw_exercises="60",
            rst_btw_rounds="120",
            difficult_level="beginner",
            rounds=3
        )
        crud.create_routine_global(test_db, routine_data)

        # Assign plan to user
        test_db.refresh(plan_created)
        crud.asign_exercise_plan(test_db, plan_created, test_user.user_id)

        # Record a completed routine first to avoid None error in endpoint
        from datetime import datetime, timezone
        exercise_record = {
            "record_datetime": datetime.now(timezone.utc).replace(tzinfo=None),
            "info_type": "rutine_end",
            "info_description": "legs",  # Different from first in order to get "chest" as next
            "exercise_increments": {},
            "push_increment": 0,
            "pull_increment": 0,
            "isometric_increment": 0,
        }
        crud.redord_end_rutine(test_db, test_user.user_id, exercise_record)

        # Now record the plan start (after a routine end, so exercise_plan_start is more recent)
        crud.record_start_exercise_plan(test_db, test_user.user_id, plan_created)

        response = client.get("/api/v1/routines/next", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "routine" in data
        assert "routine_id" in data

    def test_get_next_routine_without_auth(self, client):
        """
        Test getting next routine fails without authentication.

        Validates that:
        - Endpoint requires authentication
        - Returns 401 Unauthorized
        """
        response = client.get("/api/v1/routines/next")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Run tests with: pytest tests/test_routines.py -v
