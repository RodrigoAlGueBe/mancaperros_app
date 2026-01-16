"""Create workout_events table with Single Table Inheritance

HIGH-08: Refactor User_Tracker polymorphic table

This migration creates the new workout_events table that uses SQLAlchemy's
Single Table Inheritance pattern to replace the overloaded users_tracker table.

The old users_tracker table is preserved for backward compatibility during
the migration period.

Revision ID: high08_workout_events
Revises: (your latest revision)
Create Date: 2026-01-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'high08_workout_events'
down_revision: Union[str, None] = 'a2b3c4d5e6f7'  # After add_additional_database_indexes
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create the workout_events table for polymorphic event storage.

    This table uses Single Table Inheritance where:
    - event_type is the discriminator column
    - All event-specific columns are nullable at the table level
    - SQLAlchemy handles type-specific validation at the ORM level
    """
    op.create_table(
        'workout_events',
        # Common columns for all event types
        sa.Column('event_id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),

        # Columns for RoutineCompletedEvent
        sa.Column('routine_group', sa.String(255), nullable=True),
        sa.Column('exercise_increments', sa.JSON(), nullable=True),
        sa.Column('push_increment', sa.Integer(), nullable=True, default=0),
        sa.Column('pull_increment', sa.Integer(), nullable=True, default=0),
        sa.Column('isometric_increment', sa.Integer(), nullable=True, default=0),
        sa.Column('push_time_increment', sa.Integer(), nullable=True, default=0),
        sa.Column('pull_time_increment', sa.Integer(), nullable=True, default=0),
        sa.Column('isometric_time_increment', sa.Integer(), nullable=True, default=0),

        # Columns for ExercisePlan events
        sa.Column('exercise_plan_id', sa.Integer(), nullable=True),

        # Constraints
        sa.PrimaryKeyConstraint('event_id'),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.user_id'],
            ondelete='CASCADE'
        ),
    )

    # Create indexes for common query patterns
    op.create_index(
        'ix_workout_events_event_id',
        'workout_events',
        ['event_id']
    )
    op.create_index(
        'ix_workout_events_user_id',
        'workout_events',
        ['user_id']
    )
    op.create_index(
        'ix_workout_events_event_type',
        'workout_events',
        ['event_type']
    )
    op.create_index(
        'ix_workout_events_timestamp',
        'workout_events',
        ['timestamp']
    )
    op.create_index(
        'ix_workout_events_routine_group',
        'workout_events',
        ['routine_group']
    )
    op.create_index(
        'ix_workout_events_exercise_plan_id',
        'workout_events',
        ['exercise_plan_id']
    )

    # Composite index for common query: user + type + timestamp
    op.create_index(
        'ix_workout_events_user_type_timestamp',
        'workout_events',
        ['user_id', 'event_type', 'timestamp']
    )


def downgrade() -> None:
    """
    Remove the workout_events table.

    Note: This will permanently delete any data in the new table.
    The legacy users_tracker table will remain intact.
    """
    op.drop_index('ix_workout_events_user_type_timestamp', table_name='workout_events')
    op.drop_index('ix_workout_events_exercise_plan_id', table_name='workout_events')
    op.drop_index('ix_workout_events_routine_group', table_name='workout_events')
    op.drop_index('ix_workout_events_timestamp', table_name='workout_events')
    op.drop_index('ix_workout_events_event_type', table_name='workout_events')
    op.drop_index('ix_workout_events_user_id', table_name='workout_events')
    op.drop_index('ix_workout_events_event_id', table_name='workout_events')
    op.drop_table('workout_events')
