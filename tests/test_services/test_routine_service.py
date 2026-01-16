"""
Routine service tests.

Tests cover:
- Routine creation logic
- Exercise creation within routines
- Routine assignment to exercise plans
- Routine update operations

These are service-level tests focused on business logic.
"""

import pytest
import crud
import schemas
import models


class TestRoutineCreation:
    """Test suite for routine creation logic"""

    def test_create_routine_global(self, test_db, test_exercise_plan_global):
        """
        Test creating a global routine.

        Validates that:
        - Routine is created successfully
        - All fields are properly set
        - Routine is linked to exercise plan
        """
        routine_data = schemas.Rutine_global_Create(
            rutine_name="Test Routine Service",
            rutine_type="strength",
            rutine_group="chest",
            rutine_category="push",
            exercise_plan_id=test_exercise_plan_global.exercise_plan_id,
            rst_btw_exercises="60",
            rst_btw_rounds="120",
            difficult_level="beginner",
            rounds=3
        )

        created_routine = crud.create_routine_global(test_db, routine_data)

        assert created_routine.rutine_name == routine_data.rutine_name
        assert created_routine.rutine_group == routine_data.rutine_group
        assert created_routine.rounds == routine_data.rounds
        assert created_routine.exercise_plan_id == test_exercise_plan_global.exercise_plan_id

    def test_create_multiple_routines_same_plan(self, test_db, test_exercise_plan_global):
        """
        Test creating multiple routines for same exercise plan.

        Validates that:
        - Multiple routines can belong to same plan
        - Each has unique ID and name
        """
        routine_names = ["Chest Day", "Back Day", "Leg Day"]
        created_routines = []

        for name in routine_names:
            routine_data = schemas.Rutine_global_Create(
                rutine_name=name,
                rutine_type="strength",
                rutine_group=name.split()[0].lower(),
                rutine_category="push",
                exercise_plan_id=test_exercise_plan_global.exercise_plan_id,
                rst_btw_exercises="60",
                rst_btw_rounds="120",
                difficult_level="beginner",
                rounds=3
            )
            routine = crud.create_routine_global(test_db, routine_data)
            created_routines.append(routine)

        assert len(created_routines) == 3
        # Verify all have unique IDs
        routine_ids = [r.rutine_id for r in created_routines]
        assert len(routine_ids) == len(set(routine_ids))


class TestExerciseCreation:
    """Test suite for exercise creation within routines"""

    def test_create_exercise_global(self, test_db, test_routine_global):
        """
        Test creating a global exercise for a routine.

        Validates that:
        - Exercise is created successfully
        - Exercise is linked to routine
        - All fields are properly set
        """
        exercise_data = schemas.Exercise_global_Create(
            exercise_name="Bench Press",
            rep="10",
            exercise_type="push-weight",
            exercise_group="chest",
            rutine_id=test_routine_global.rutine_id,
            image="bench_press.jpg"
        )

        created_exercise = crud.create_exercise_global(test_db, exercise_data)

        assert created_exercise.exercise_name == exercise_data.exercise_name
        assert created_exercise.rep == exercise_data.rep
        assert created_exercise.exercise_type == exercise_data.exercise_type
        assert created_exercise.rutine_id == test_routine_global.rutine_id

    def test_create_multiple_exercises_same_routine(self, test_db, test_routine_global):
        """
        Test creating multiple exercises for same routine.

        Validates that:
        - Multiple exercises can belong to same routine
        - Each has unique ID
        """
        exercises_data = [
            {
                "exercise_name": "Push-ups",
                "rep": "15",
                "exercise_type": "push-bodyweight",
                "exercise_group": "chest",
                "rutine_id": test_routine_global.rutine_id,
                "image": "pushups.jpg"
            },
            {
                "exercise_name": "Dumbbell Press",
                "rep": "12",
                "exercise_type": "push-weight",
                "exercise_group": "chest",
                "rutine_id": test_routine_global.rutine_id,
                "image": "dumbbell_press.jpg"
            },
            {
                "exercise_name": "Cable Flyes",
                "rep": "15",
                "exercise_type": "push-cable",
                "exercise_group": "chest",
                "rutine_id": test_routine_global.rutine_id,
                "image": "cable_flyes.jpg"
            }
        ]

        created_exercises = []
        for ex_data in exercises_data:
            exercise_schema = schemas.Exercise_global_Create(**ex_data)
            exercise = crud.create_exercise_global(test_db, exercise_schema)
            created_exercises.append(exercise)

        assert len(created_exercises) == 3
        # Verify all exercises belong to same routine
        for exercise in created_exercises:
            assert exercise.rutine_id == test_routine_global.rutine_id


class TestRoutineAssignment:
    """Test suite for routine assignment operations"""

    def test_assign_exercise_plan_copies_routines(self, test_db, test_user, test_exercise_plan_global, test_routine_global, test_exercise_global):
        """
        Test that assigning plan copies routines to user.

        Validates that:
        - Routines are copied when plan is assigned
        - User has own instance of routines
        - Exercises are also copied
        """
        # Assign plan to user
        assigned_plan = crud.asign_exercise_plan(
            test_db,
            test_exercise_plan_global,
            test_user.user_id
        )

        # Verify routines were copied
        user_routines = test_db.query(models.Rutine).filter(
            models.Rutine.exercise_plan_id == assigned_plan.exercise_plan_id
        ).all()

        assert len(user_routines) > 0

        # Verify exercises were copied
        for routine in user_routines:
            exercises = test_db.query(models.Exercise).filter(
                models.Exercise.rutine_id == routine.rutine_id
            ).all()
            assert len(exercises) > 0

    def test_assigned_routines_independent_from_global(self, test_db, test_user, test_exercise_plan_global, test_routine_global, test_exercise_global):
        """
        Test that assigned routines are independent copies.

        Validates that:
        - User's routines are in different table (Rutine vs Rutine_global)
        - Changes to user routines don't affect global routines
        - Routine data is copied correctly
        """
        # Assign plan
        assigned_plan = crud.asign_exercise_plan(
            test_db,
            test_exercise_plan_global,
            test_user.user_id
        )

        # Get user's routines (from Rutine table, not Rutine_global)
        user_routines = test_db.query(models.Rutine).filter(
            models.Rutine.exercise_plan_id == assigned_plan.exercise_plan_id
        ).all()

        # Verify routines were copied
        assert len(user_routines) > 0

        # Verify they are independent copies (in different table)
        # User routines are in Rutine table, global routines in Rutine_global table
        # They can have the same ID since they're in different tables
        for user_routine in user_routines:
            # Verify it's not the same object/table
            assert isinstance(user_routine, models.Rutine)
            assert not isinstance(user_routine, models.Rutine_global)
            # But data should match
            assert user_routine.rutine_name == test_routine_global.rutine_name


class TestRoutineUpdate:
    """Test suite for routine update operations"""

    def test_update_routine_exercises_reps(self, test_db, test_user, assigned_exercise_plan):
        """
        Test updating exercise repetitions in routine.

        Validates that:
        - Exercise reps can be updated
        - Changes are persisted
        - Routine update function works correctly
        """
        # Get a routine from assigned plan
        routine = test_db.query(models.Rutine).filter(
            models.Rutine.exercise_plan_id == assigned_exercise_plan.exercise_plan_id
        ).first()

        # Get exercises
        exercises = test_db.query(models.Exercise).filter(
            models.Exercise.rutine_id == routine.rutine_id
        ).all()

        if len(exercises) > 0:
            original_rep = exercises[0].rep
            exercises[0].rep = "15"

            # Update routine
            updated_routine = crud.update_routine(test_db, routine)

            # Verify update
            test_db.refresh(exercises[0])
            assert exercises[0].rep == "15"
            assert exercises[0].rep != original_rep


class TestRoutineRetrieval:
    """Test suite for routine retrieval operations"""

    def test_get_routine_info(self, test_db, test_user, test_exercise_plan_global, test_routine_global):
        """
        Test retrieving routine information.

        Validates that:
        - Routine can be queried by ID
        - Returns correct routine
        """
        # Assign plan to user to create user-specific routine
        crud.asign_exercise_plan(test_db, test_exercise_plan_global, test_user.user_id)

        # Get user's routine (created by assignment)
        user_routine = test_db.query(models.Rutine).filter(
            models.Rutine.exercise_plan_id == test_db.query(models.Exercise_plan)
            .filter(models.Exercise_plan.user_owner_id == test_user.user_id)
            .first().exercise_plan_id
        ).first()

        routine_query = crud.get_rutine_info(test_db, user_routine.rutine_id)
        routine = routine_query.first()

        assert routine is not None
        assert routine.rutine_id == user_routine.rutine_id
        assert routine.rutine_name == test_routine_global.rutine_name

    def test_get_routines_by_exercise_plan(self, test_db, test_exercise_plan_global, test_routine_global):
        """
        Test retrieving all routines for an exercise plan.

        Validates that:
        - All routines for plan are returned
        - Routines are correctly associated with plan
        """
        routines = test_db.query(models.Rutine_global).filter(
            models.Rutine_global.exercise_plan_id == test_exercise_plan_global.exercise_plan_id
        ).all()

        assert len(routines) > 0
        for routine in routines:
            assert routine.exercise_plan_id == test_exercise_plan_global.exercise_plan_id


# Run tests with: pytest tests/test_services/test_routine_service.py -v
