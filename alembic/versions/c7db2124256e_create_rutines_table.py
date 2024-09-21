"""create rutines table

Revision ID: c7db2124256e
Revises: 534e08627f7a
Create Date: 2023-10-20 17:51:00.394142

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7db2124256e'
down_revision = '534e08627f7a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'rutines',
        sa.Column('rutine_id', sa.Integer, primary_key=True, index=True),
        sa.Column('rutine_name', sa.String(50), nullable=False, unique=False, index=True, default="New rutine name"),
        sa.Column('rutine_type', sa.String(50), nullable=False, unique=False, index=True, default="New rutine type"),
        sa.Column('rutine_group', sa.String(50), nullable=False, unique=False, index=True, default="New rutine group"),
        sa.Column('rutine_category', sa.String(50), nullable=False, unique=False, index=True, default="New rutine category"),
        sa.Column('exercise_plan_id', sa.Integer, sa.ForeignKey('exercise_plans.exercise_plan_id'), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("rutines")
