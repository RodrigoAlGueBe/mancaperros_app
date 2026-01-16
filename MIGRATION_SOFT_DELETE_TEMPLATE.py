"""
TEMPLATE: Alembic migration for adding soft delete columns.

This is a TEMPLATE file showing how to create the migration for soft delete.
Run: alembic revision --autogenerate -m "add soft delete columns"

The autogenerate should detect the new columns from the models.
If not, use this template to create the migration manually.

Location: alembic/versions/XXXX_add_soft_delete_columns.py
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'xxxx_add_soft_delete_columns'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add soft delete columns to all main models."""

    # Users table
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('is_deleted', sa.Boolean(), server_default=sa.false(), nullable=False))
    op.create_index(op.f('ix_users_deleted_at'), 'users', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_users_is_deleted'), 'users', ['is_deleted'], unique=False)

    # Exercise Plans table
    op.add_column('exercise_plans', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('exercise_plans', sa.Column('is_deleted', sa.Boolean(), server_default=sa.false(), nullable=False))
    op.create_index(op.f('ix_exercise_plans_deleted_at'), 'exercise_plans', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_exercise_plans_is_deleted'), 'exercise_plans', ['is_deleted'], unique=False)

    # Routines table
    op.add_column('rutines', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('rutines', sa.Column('is_deleted', sa.Boolean(), server_default=sa.false(), nullable=False))
    op.create_index(op.f('ix_rutines_deleted_at'), 'rutines', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_rutines_is_deleted'), 'rutines', ['is_deleted'], unique=False)

    # Exercises table
    op.add_column('exercises', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('exercises', sa.Column('is_deleted', sa.Boolean(), server_default=sa.false(), nullable=False))
    op.create_index(op.f('ix_exercises_deleted_at'), 'exercises', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_exercises_is_deleted'), 'exercises', ['is_deleted'], unique=False)


def downgrade() -> None:
    """Remove soft delete columns from all tables."""

    # Exercises table
    op.drop_index(op.f('ix_exercises_is_deleted'), table_name='exercises')
    op.drop_index(op.f('ix_exercises_deleted_at'), table_name='exercises')
    op.drop_column('exercises', 'is_deleted')
    op.drop_column('exercises', 'deleted_at')

    # Routines table
    op.drop_index(op.f('ix_rutines_is_deleted'), table_name='rutines')
    op.drop_index(op.f('ix_rutines_deleted_at'), table_name='rutines')
    op.drop_column('rutines', 'is_deleted')
    op.drop_column('rutines', 'deleted_at')

    # Exercise Plans table
    op.drop_index(op.f('ix_exercise_plans_is_deleted'), table_name='exercise_plans')
    op.drop_index(op.f('ix_exercise_plans_deleted_at'), table_name='exercise_plans')
    op.drop_column('exercise_plans', 'is_deleted')
    op.drop_column('exercise_plans', 'deleted_at')

    # Users table
    op.drop_index(op.f('ix_users_is_deleted'), table_name='users')
    op.drop_index(op.f('ix_users_deleted_at'), table_name='users')
    op.drop_column('users', 'is_deleted')
    op.drop_column('users', 'deleted_at')
