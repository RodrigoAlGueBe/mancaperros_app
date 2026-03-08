"""Add composite index user_owner_id + exercise_plan_id

Revision ID: a1b2c3d4e5f6
Revises: 0e72225126e6
Create Date: 2025-03-02 12:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '0e72225126e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create composite index for optimized user + plan queries
    op.create_index(
        'ix_exercise_plans_user_plan',
        'exercise_plans',
        ['user_owner_id', 'exercise_plan_id'],
        unique=False
    )


def downgrade() -> None:
    # Remove composite index
    op.drop_index('ix_exercise_plans_user_plan', table_name='exercise_plans')
