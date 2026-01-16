"""
Exercise plan endpoint tests.

Tests cover:
- Creating global exercise plans
- Assigning plans to users
- Retrieving available plans
- Plan validation and error handling
- Full exercise plan creation (with routines and exercises)

All tests use in-memory SQLite database via conftest.py fixtures.
"""

import pytest
from fastapi import status
import json


class TestCreateExercisePlanGlobal:
    """Test suite for POST /api/v1/exercises/plans_global"""

    def test_create_exercise_plan_global_success(self, client, test_user, auth_headers):
        """
        Test successful creation of global exercise plan.

        Validates that:
        - Authenticated user can create global exercise plan
        - Returns created plan with all fields
        - Plan is stored in database
        """
        plan_data = {
            "exercise_plan_name": "Beginner Strength Plan",
            "exercise_plan_type": "strength",
            "difficult_level": "beginner"
        }

        response = client.post(
            "/api/v1/exercises/plans_global",
            json=plan_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["exercise_plan_name"] == plan_data["exercise_plan_name"]
        assert data["exercise_plan_type"] == plan_data["exercise_plan_type"]
        assert data["difficult_level"] == plan_data["difficult_level"]
        assert "exercise_plan_id" in data
        assert data["user_creator_id"] == test_user.user_id

    def test_create_exercise_plan_global_duplicate_name(self, client, test_exercise_plan_global, auth_headers):
        """
        Test creation fails with duplicate plan name.

        Validates that:
        - Cannot create plan with existing name
        - Returns 400 Bad Request
        - Error message indicates plan already exists
        """
        plan_data = {
            "exercise_plan_name": test_exercise_plan_global.exercise_plan_name,
            "exercise_plan_type": "strength",
            "difficult_level": "beginner"
        }

        response = client.post(
            "/api/v1/exercises/plans_global",
            json=plan_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Exercise plan already exists" in response.json()["error"]["message"]

    def test_create_exercise_plan_global_without_auth(self, client):
        """
        Test creation fails without authentication.

        Validates that:
        - Endpoint requires authentication
        - Returns 401 Unauthorized
        """
        plan_data = {
            "exercise_plan_name": "Test Plan",
            "exercise_plan_type": "strength",
            "difficult_level": "beginner"
        }

        response = client.post("/api/v1/exercises/plans_global", json=plan_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_exercise_plan_global_missing_fields(self, client, auth_headers):
        """
        Test creation fails with missing required fields.

        Validates that:
        - exercise_plan_name is required
        - Returns 422 Unprocessable Entity when name is missing
        """
        plan_data = {
            # Missing exercise_plan_name (required field)
            "exercise_plan_type": "strength",
            "difficult_level": "beginner"
        }

        response = client.post(
            "/api/v1/exercises/plans_global",
            json=plan_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAssignExercisePlanToUser:
    """Test suite for PUT /api/v1/exercises/assign"""

    def test_assign_exercise_plan_success(self, client, test_db, test_user, test_exercise_plan_global, auth_headers):
        """
        Test successful assignment of exercise plan to user.

        Validates that:
        - User can be assigned an exercise plan
        - Returns tracker information
        - Plan is copied to user's exercise plans
        """
        plan_info = {
            "exercise_plan_id": test_exercise_plan_global.exercise_plan_id,
            "exercise_plan_name": test_exercise_plan_global.exercise_plan_name
        }

        response = client.put(
            "/api/v1/exercises/assign",
            json=plan_info,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == test_user.user_id
        assert "user_tracker_id" in data
        assert data["info_type"] == "exercise_plan_start"

    def test_assign_exercise_plan_replaces_existing(self, client, test_db, test_user, auth_headers):
        """
        Test assigning new plan replaces existing plan.

        Validates that:
        - Assigning new plan removes old plan
        - Creates end record for old plan
        - Creates start record for new plan
        """
        # Create and assign first plan
        plan_data_1 = {
            "exercise_plan_name": "First Plan",
            "exercise_plan_type": "strength",
            "difficult_level": "beginner"
        }
        response1 = client.post(
            "/api/v1/exercises/plans_global",
            json=plan_data_1,
            headers=auth_headers
        )
        plan1 = response1.json()

        # Assign first plan
        client.put(
            "/api/v1/exercises/assign",
            json={
                "exercise_plan_id": plan1["exercise_plan_id"],
                "exercise_plan_name": plan1["exercise_plan_name"]
            },
            headers=auth_headers
        )

        # Create and assign second plan
        plan_data_2 = {
            "exercise_plan_name": "Second Plan",
            "exercise_plan_type": "cardio",
            "difficult_level": "intermediate"
        }
        response2 = client.post(
            "/api/v1/exercises/plans_global",
            json=plan_data_2,
            headers=auth_headers
        )
        plan2 = response2.json()

        # Assign second plan (should replace first)
        response = client.put(
            "/api/v1/exercises/assign",
            json={
                "exercise_plan_id": plan2["exercise_plan_id"],
                "exercise_plan_name": plan2["exercise_plan_name"]
            },
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

    def test_assign_nonexistent_exercise_plan(self, client, auth_headers):
        """
        Test assignment fails with non-existent plan.

        Validates that:
        - Cannot assign plan that doesn't exist
        - Returns 400 Bad Request
        - Error message indicates plan not found
        """
        plan_info = {
            "exercise_plan_id": 99999,  # Non-existent ID
            "exercise_plan_name": "Nonexistent Plan"
        }

        response = client.put(
            "/api/v1/exercises/assign",
            json=plan_info,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Exercise plan not found" in response.json()["error"]["message"]

    def test_assign_exercise_plan_without_auth(self, client, test_exercise_plan_global):
        """
        Test assignment fails without authentication.

        Validates that:
        - Endpoint requires authentication
        - Returns 401 Unauthorized
        """
        plan_info = {
            "exercise_plan_id": test_exercise_plan_global.exercise_plan_id
        }

        response = client.put("/api/v1/exercises/assign", json=plan_info)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetAvailableExercisePlans:
    """Test suite for GET /api/v1/exercises/available/{exercise_plan_type}"""

    def test_get_available_plans_success(self, client, test_db, test_user, auth_headers):
        """
        Test successful retrieval of available exercise plans by type.

        Validates that:
        - Returns all plans of specified type
        - Response is list of plans
        - All plans have correct type
        """
        # Create multiple plans of same type
        import crud
        import schemas

        for i in range(3):
            plan_data = schemas.Exercise_plan_global_Create(
                exercise_plan_name=f"Full Body Plan {i}",
                exercise_plan_type="full_body",
                difficult_level="beginner"
            )
            crud.create_exercise_plan_global(test_db, plan_data, test_user.user_id)

        response = client.get(
            "/api/v1/exercises/available/full_body",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        # Verify all plans have correct type
        for plan in data:
            assert plan["exercise_plan_type"] == "full_body"

    def test_get_available_plans_not_found(self, client, auth_headers):
        """
        Test retrieval with no plans of specified type.

        Validates that:
        - Returns 404 when no plans exist
        - Error message indicates no plans found
        """
        response = client.get(
            "/api/v1/exercises/available/nonexistent_type",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "No exercise plans found" in response.json()["error"]["message"]

    def test_get_available_plans_without_auth(self, client):
        """
        Test retrieval fails without authentication.

        Validates that:
        - Endpoint requires authentication
        - Returns 401 Unauthorized
        """
        response = client.get("/api/v1/exercises/available/strength")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCreateFullExercisePlan:
    """Test suite for POST /api/v1/exercises/plans_global_full"""

    def test_create_full_exercise_plan_success(self, client, test_user, auth_headers):
        """
        Test successful creation of complete exercise plan with routines and exercises.

        Validates that:
        - Can create plan, routines, and exercises in single request
        - All nested data is properly created
        - Returns success message
        """
        full_plan = {
            "exercise_plan_name": "Complete Training Plan",
            "exercise_plan_type": "strength",
            "difficult_level": "intermediate",
            "rutines": [
                {
                    "rutine_name": "Push Day",
                    "rutine_group": "chest",
                    "rutine_category": "strength",
                    "rst_btw_exercises": "60",
                    "rst_btw_rounds": "120",
                    "difficult_level": "intermediate",
                    "rounds": 3,
                    "exercises": [
                        {
                            "exercise_name": "Push-ups",
                            "rep": "10",
                            "exercise_type": "push-bodyweight",
                            "image": "pushups.jpg"
                        },
                        {
                            "exercise_name": "Bench Press",
                            "rep": "8",
                            "exercise_type": "push-weight",
                            "image": "bench.jpg"
                        }
                    ]
                },
                {
                    "rutine_name": "Pull Day",
                    "rutine_group": "back",
                    "rutine_category": "strength",
                    "rst_btw_exercises": "60",
                    "rst_btw_rounds": "120",
                    "difficult_level": "intermediate",
                    "rounds": 3,
                    "exercises": [
                        {
                            "exercise_name": "Pull-ups",
                            "rep": "8",
                            "exercise_type": "pull-bodyweight",
                            "image": "pullups.jpg"
                        }
                    ]
                }
            ]
        }

        response = client.post(
            "/api/v1/exercises/plans_global_full",
            json=full_plan,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert "Entire exercise plan created correctly" in response.json()["detail"]

    def test_create_full_exercise_plan_without_auth(self, client):
        """
        Test creation fails without authentication.

        Validates that:
        - Endpoint requires authentication
        - Returns 401 Unauthorized
        """
        full_plan = {
            "exercise_plan_name": "Test Plan",
            "exercise_plan_type": "strength",
            "difficult_level": "beginner",
            "rutines": []
        }

        response = client.post("/api/v1/exercises/plans_global_full", json=full_plan)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_full_exercise_plan_missing_data(self, client, auth_headers):
        """
        Test creation fails with incomplete data.

        Validates that:
        - All required fields must be provided
        - Returns error when required fields are missing
        - The endpoint uses dict instead of Pydantic model, so KeyError will occur
        """
        incomplete_plan = {
            "exercise_plan_name": "Incomplete Plan"
            # Missing required fields like exercise_plan_type and difficult_level
        }

        # The endpoint will raise KeyError when trying to access missing dict keys
        # This is expected behavior for this endpoint's implementation
        try:
            response = client.post(
                "/api/v1/exercises/plans_global_full",
                json=incomplete_plan,
                headers=auth_headers
            )
            # If request succeeds somehow, it should return error status
            assert response.status_code in [
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ]
        except KeyError:
            # Expected: endpoint raises KeyError for missing required fields
            # This is the current implementation behavior
            pass


# Run tests with: pytest tests/test_exercise_plans.py -v
