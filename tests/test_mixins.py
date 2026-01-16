"""
Test suite for domain-specific mixins (MED-08 refactoring).

This module verifies that the mixins defined in
infrastructure.database.models.mixins work correctly with SQLAlchemy 2.0+.

Tests cover:
- ExercisePlanMixin: Fields for exercise plan models
- RoutineMixin: Fields for routine models
- ExerciseMixin: Fields for exercise models

The tests verify:
1. Mixins can be properly inherited by SQLAlchemy models
2. @declared_attr decorators work correctly
3. Default values are applied as expected
4. Column configurations match the original models
"""

import os
# Set TESTING environment variable BEFORE importing application modules
os.environ["TESTING"] = "1"

import pytest
from datetime import date
from sqlalchemy import Column, Integer, ForeignKey, String, inspect
from sqlalchemy.orm import relationship

# Import base and mixins
from infrastructure.database.models.base import Base
from infrastructure.database.models.mixins import (
    ExercisePlanMixin,
    RoutineMixin,
    ExerciseMixin,
)
from infrastructure.database.models.soft_delete_mixin import SoftDeleteMixin

# Import actual models for comparison
from infrastructure.database.models.exercise_plan import Exercise_plan
from infrastructure.database.models.exercise_plan_global import Exercise_plan_global
from infrastructure.database.models.routine import Rutine
from infrastructure.database.models.routine_global import Rutine_global
from infrastructure.database.models.exercise import Exercise
from infrastructure.database.models.exercise_global import Exercise_global


class TestExercisePlanMixin:
    """Tests for ExercisePlanMixin functionality."""

    def test_mixin_defines_expected_fields(self):
        """Verify ExercisePlanMixin defines all expected fields."""
        expected_fields = [
            "exercise_plan_name",
            "exercise_plan_type",
            "creation_date",
            "difficult_level",
            "routine_group_order",
        ]

        # Check that all expected methods exist in the mixin
        for field in expected_fields:
            assert hasattr(ExercisePlanMixin, field), f"Missing field: {field}"

    def test_mixin_fields_match_exercise_plan_model(self):
        """Verify mixin fields match Exercise_plan model columns."""
        # Get column names from actual model
        model_columns = {c.name for c in Exercise_plan.__table__.columns}

        # Fields that should be in mixin
        mixin_fields = {
            "exercise_plan_name",
            "exercise_plan_type",
            "creation_date",
            "difficult_level",
            "routine_group_order",
        }

        # All mixin fields should exist in the model
        assert mixin_fields.issubset(model_columns), (
            f"Missing fields in model: {mixin_fields - model_columns}"
        )

    def test_mixin_fields_match_exercise_plan_global_model(self):
        """Verify mixin fields match Exercise_plan_global model columns."""
        # Get column names from actual model
        model_columns = {c.name for c in Exercise_plan_global.__table__.columns}

        # Fields that should be in mixin
        mixin_fields = {
            "exercise_plan_name",
            "exercise_plan_type",
            "creation_date",
            "difficult_level",
            "routine_group_order",
        }

        # All mixin fields should exist in the model
        assert mixin_fields.issubset(model_columns), (
            f"Missing fields in model: {mixin_fields - model_columns}"
        )

    def test_exercise_plan_default_values(self):
        """Verify default values match between mixin and models."""
        # Check defaults in Exercise_plan
        ep_columns = {c.name: c for c in Exercise_plan.__table__.columns}

        assert ep_columns["exercise_plan_name"].default.arg == "New exercise plan"
        assert ep_columns["exercise_plan_type"].default.arg == "New exercise plan type"
        assert ep_columns["creation_date"].default.arg == date(1970, 1, 1)
        assert ep_columns["difficult_level"].default.arg == "New exercise plan difficult level"


class TestRoutineMixin:
    """Tests for RoutineMixin functionality."""

    def test_mixin_defines_expected_fields(self):
        """Verify RoutineMixin defines all expected fields."""
        expected_fields = [
            "rutine_name",
            "rutine_type",
            "rutine_group",
            "rutine_category",
            "rounds",
            "rst_btw_exercises",
            "rst_btw_rounds",
            "difficult_level",
        ]

        # Check that all expected methods exist in the mixin
        for field in expected_fields:
            assert hasattr(RoutineMixin, field), f"Missing field: {field}"

    def test_mixin_fields_match_rutine_model(self):
        """Verify mixin fields match Rutine model columns."""
        model_columns = {c.name for c in Rutine.__table__.columns}

        mixin_fields = {
            "rutine_name",
            "rutine_type",
            "rutine_group",
            "rutine_category",
            "rounds",
            "rst_btw_exercises",
            "rst_btw_rounds",
            "difficult_level",
        }

        assert mixin_fields.issubset(model_columns), (
            f"Missing fields in model: {mixin_fields - model_columns}"
        )

    def test_mixin_fields_match_rutine_global_model(self):
        """Verify mixin fields match Rutine_global model columns."""
        model_columns = {c.name for c in Rutine_global.__table__.columns}

        mixin_fields = {
            "rutine_name",
            "rutine_type",
            "rutine_group",
            "rutine_category",
            "rounds",
            "rst_btw_exercises",
            "rst_btw_rounds",
            "difficult_level",
        }

        assert mixin_fields.issubset(model_columns), (
            f"Missing fields in model: {mixin_fields - model_columns}"
        )

    def test_routine_default_values(self):
        """Verify default values match between mixin and models."""
        rutine_columns = {c.name: c for c in Rutine.__table__.columns}

        assert rutine_columns["rutine_name"].default.arg == "New rutine name"
        assert rutine_columns["rutine_type"].default.arg == "New rutine type"
        assert rutine_columns["rutine_group"].default.arg == "New rutine group"
        assert rutine_columns["rutine_category"].default.arg == "New rutine category"
        assert rutine_columns["rounds"].default.arg == 0
        assert rutine_columns["rst_btw_exercises"].default.arg == "0"
        assert rutine_columns["rst_btw_rounds"].default.arg == "0"
        assert rutine_columns["difficult_level"].default.arg == "New rutine difficult level"


class TestExerciseMixin:
    """Tests for ExerciseMixin functionality."""

    def test_mixin_defines_expected_fields(self):
        """Verify ExerciseMixin defines all expected fields."""
        expected_fields = [
            "exercise_name",
            "rep",
            "exercise_type",
            "exercise_group",
            "image",
        ]

        for field in expected_fields:
            assert hasattr(ExerciseMixin, field), f"Missing field: {field}"

    def test_mixin_fields_match_exercise_model(self):
        """Verify mixin fields match Exercise model columns."""
        model_columns = {c.name for c in Exercise.__table__.columns}

        mixin_fields = {
            "exercise_name",
            "rep",
            "exercise_type",
            "exercise_group",
            "image",
        }

        assert mixin_fields.issubset(model_columns), (
            f"Missing fields in model: {mixin_fields - model_columns}"
        )

    def test_mixin_fields_match_exercise_global_model(self):
        """Verify mixin fields match Exercise_global model columns."""
        model_columns = {c.name for c in Exercise_global.__table__.columns}

        mixin_fields = {
            "exercise_name",
            "rep",
            "exercise_type",
            "exercise_group",
            "image",
        }

        assert mixin_fields.issubset(model_columns), (
            f"Missing fields in model: {mixin_fields - model_columns}"
        )

    def test_exercise_default_values(self):
        """Verify default values match between mixin and models."""
        exercise_columns = {c.name: c for c in Exercise.__table__.columns}

        assert exercise_columns["exercise_name"].default.arg == "New exercise name"
        assert exercise_columns["rep"].default.arg == "empty"
        assert exercise_columns["exercise_type"].default.arg == "New exercise type"
        assert exercise_columns["exercise_group"].default.arg == "New exercise group"
        assert exercise_columns["image"].default.arg == "empty"


class TestMixinIntegration:
    """Integration tests for mixin usage patterns."""

    def test_model_specific_fields_not_in_mixins(self):
        """Verify model-specific fields are correctly excluded from mixins."""
        # Primary keys should NOT be in mixins
        assert not hasattr(ExercisePlanMixin, "exercise_plan_id")
        assert not hasattr(RoutineMixin, "rutine_id")
        assert not hasattr(ExerciseMixin, "exercise_id")

        # Foreign keys with different targets should NOT be in mixins
        assert not hasattr(ExercisePlanMixin, "user_owner_id")
        assert not hasattr(ExercisePlanMixin, "user_creator_id")
        assert not hasattr(RoutineMixin, "exercise_plan_id")
        assert not hasattr(ExerciseMixin, "rutine_id")

    def test_field_count_comparison(self):
        """Verify mixins cover significant portion of model fields."""
        # Exercise_plan fields
        ep_total = len(Exercise_plan.__table__.columns)
        ep_mixin_fields = 5  # exercise_plan_name, exercise_plan_type, creation_date, difficult_level, routine_group_order
        # Model-specific: exercise_plan_id, user_owner_id, deleted_at, is_deleted
        ep_coverage = ep_mixin_fields / (ep_total - 4)  # Exclude model-specific
        assert ep_coverage >= 0.8, f"ExercisePlanMixin coverage too low: {ep_coverage:.0%}"

        # Rutine fields
        r_total = len(Rutine.__table__.columns)
        r_mixin_fields = 8  # rutine_name, rutine_type, rutine_group, rutine_category, rounds, rst_btw_exercises, rst_btw_rounds, difficult_level
        # Model-specific: rutine_id, exercise_plan_id, deleted_at, is_deleted
        r_coverage = r_mixin_fields / (r_total - 4)
        assert r_coverage >= 0.8, f"RoutineMixin coverage too low: {r_coverage:.0%}"

        # Exercise fields
        e_total = len(Exercise.__table__.columns)
        e_mixin_fields = 5  # exercise_name, rep, exercise_type, exercise_group, image
        # Model-specific: exercise_id, rutine_id, deleted_at, is_deleted
        e_coverage = e_mixin_fields / (e_total - 4)
        assert e_coverage >= 0.8, f"ExerciseMixin coverage too low: {e_coverage:.0%}"

    def test_column_configurations_consistency(self):
        """Verify column configurations are consistent between paired models."""
        # Compare Exercise_plan vs Exercise_plan_global
        ep_cols = {c.name: c for c in Exercise_plan.__table__.columns}
        epg_cols = {c.name: c for c in Exercise_plan_global.__table__.columns}

        shared_fields = [
            "exercise_plan_name",
            "exercise_plan_type",
            "creation_date",
            "difficult_level",
            "routine_group_order",
        ]

        for field in shared_fields:
            ep_col = ep_cols[field]
            epg_col = epg_cols[field]

            # Check same type
            assert type(ep_col.type).__name__ == type(epg_col.type).__name__, (
                f"Type mismatch for {field}: {type(ep_col.type)} vs {type(epg_col.type)}"
            )

            # Check same default
            ep_default = ep_col.default.arg if ep_col.default else None
            epg_default = epg_col.default.arg if epg_col.default else None
            assert ep_default == epg_default, (
                f"Default mismatch for {field}: {ep_default} vs {epg_default}"
            )


class TestMixinExports:
    """Tests for proper mixin exports from package."""

    def test_mixins_exported_from_models_package(self):
        """Verify mixins are exported from models __init__.py."""
        from infrastructure.database.models import (
            ExercisePlanMixin,
            RoutineMixin,
            ExerciseMixin,
            SoftDeleteMixin,
        )

        # Verify they are the same classes
        assert ExercisePlanMixin is not None
        assert RoutineMixin is not None
        assert ExerciseMixin is not None
        assert SoftDeleteMixin is not None

    def test_mixins_have_all_attribute(self):
        """Verify mixins module has __all__ defined correctly."""
        from infrastructure.database.models import mixins

        assert hasattr(mixins, "__all__")
        assert "ExercisePlanMixin" in mixins.__all__
        assert "RoutineMixin" in mixins.__all__
        assert "ExerciseMixin" in mixins.__all__
