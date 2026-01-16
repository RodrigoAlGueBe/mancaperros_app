"""Fix typo in Exercise class names (no database changes)

This migration documents the correction of a typo in Python class names:
- Exsercise -> Exercise
- Exsercise_global -> Exercise_global

The database table names remain unchanged:
- 'exercises' table (not renamed)
- 'exercises_global' table (not renamed)

This is a code-only change that does not affect the database schema.

Revision ID: a1b2c3d4e5f6
Revises: 0e72225126e6
Create Date: 2026-01-09 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '0e72225126e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No database changes required
    # This migration documents the correction of Python class names:
    # - models.Exsercise -> models.Exercise (tablename still 'exercises')
    # - models.Exsercise_global -> models.Exercise_global (tablename still 'exercises_global')
    pass


def downgrade() -> None:
    # No database changes required
    # Rolling back this migration only affects Python code, not the database
    pass
