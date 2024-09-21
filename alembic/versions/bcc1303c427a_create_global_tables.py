"""Create global tables

Revision ID: bcc1303c427a
Revises: 29e535bc8e01
Create Date: 2024-09-18 18:54:57.962391

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bcc1303c427a'
down_revision = '29e535bc8e01'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'exercise_plans_global',
        sa.Column('exercise_plan_id', sa.Integer, primary_key=True, index=True),
        sa.Column('exercise_plan_name', sa.String(50), nullable=False, unique=False, index=True, default="New exercise plan"),
        sa.Column('user_creator_id', sa.Integer, sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('exercise_plan_type', sa.String(50), nullable=False, unique=False, index=True, default="New exercise plan type"),
        sa.Column('creation_date', sa.Date, nullable=False, unique=False, index=True, default=sa.func.now()),
        sa.Column('difficult_level', sa.String(50), nullable=False, unique=False, index=True, default="New exercise plan difficult level"),
    )

    op.create_table(
        'rutines_global',
        sa.Column('rutine_id', sa.Integer, primary_key=True, index=True),
        sa.Column('rutine_name', sa.String(50), nullable=False, unique=False, index=True, default="New rutine name"),
        sa.Column('rutine_type', sa.String(50), nullable=False, unique=False, index=True, default="New rutine type"),
        sa.Column('rutine_group', sa.String(50), nullable=False, unique=False, index=True, default="New rutine group"),
        sa.Column('rutine_category', sa.String(50), nullable=False, unique=False, index=True, default="New rutine category"),
        sa.Column('exercise_plan_id', sa.Integer, sa.ForeignKey('exercise_plans_global.exercise_plan_id'), nullable=False),
        sa.Column('rounds', sa.Integer, nullable=False, unique=False, index=True, default=0),
        sa.Column('rst_btw_exercises', sa.String(50), nullable=False, unique=False, index=True, default="0"),
        sa.Column('rst_btw_rounds', sa.String(50), nullable=False, unique=False, index=True, default="0"),
        sa.Column('difficult_level', sa.String(50), nullable=False, unique=False, index=True, default="New rutine difficult level"),
    )

    op.create_table(
        'exercises_global',
        sa.Column('exercise_id', sa.Integer, primary_key=True, index=True),
        sa.Column('exercise_name', sa.String(50), nullable=False, unique=False, index=True, default="New exercise name"),
        sa.Column('rep', sa.String(50), nullable=False, unique=False, index=True, default="empty"),
        sa.Column('exercise_type', sa.String(50), nullable=False, unique=False, index=True, default="New exercise type"),
        sa.Column('exercise_group', sa.String(50), nullable=False, unique=False, index=True, default="New exercise group"),
        sa.Column('rutine_id', sa.Integer, sa.ForeignKey('rutines_global.rutine_id'), nullable=False),
        sa.Column('image', sa.String(50), nullable=False, unique=False, index=True, default="empty"),
    )


def downgrade() -> None:
    op.drop_table("exercise_plans_global")
    op.drop_table("rutines_global")
    op.drop_table("exercises_global")
