"""create exercise_plans table

Revision ID: 534e08627f7a
Revises: 9e559d7147e3
Create Date: 2023-10-20 17:50:48.478407

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '534e08627f7a'
down_revision = '9e559d7147e3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'exercise_plans',
        sa.Column('exercise_plan_id', sa.Integer, primary_key=True, index=True),
        sa.Column('exercise_plan_name', sa.String(50), nullable=False, unique=False, index=True, default="New exercise plan"),
        sa.Column('user_owner_id', sa.Integer, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("exercise_plans")
