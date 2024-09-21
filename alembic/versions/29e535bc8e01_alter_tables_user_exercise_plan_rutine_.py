"""alter tables User, Exercise_plan, Rutine, Exsercise

Revision ID: 29e535bc8e01
Revises: 833907672c2f
Create Date: 2024-09-09 11:22:53.521939

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '29e535bc8e01'
down_revision = '833907672c2f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('user_image', sa.String, unique=False, index=True, default="empty"))
    op.add_column('exercise_plans', sa.Column('exercise_plan_type', sa.String, unique=False, index=True, default="New exercise plan type"))
    op.add_column('exercise_plans', sa.Column('creation_date', sa.Date, unique=False, index=True, default="1970-01-01"))
    op.add_column('exercise_plans', sa.Column('difficult_level', sa.String, unique=False, index=True, default="New exercise plan difficult level"))
    op.add_column('rutines', sa.Column('rounds', sa.Integer, unique=False, index=True, default=0))
    op.add_column('rutines', sa.Column('rst_btw_exercises', sa.String, unique=False, index=True, default="0"))
    op.add_column('rutines', sa.Column('rst_btw_rounds', sa.String, unique=False, index=True, default="0"))
    op.add_column('rutines', sa.Column('difficult_level', sa.String, unique=False, index=True, default="New rutine difficult level"))
    op.add_column('exercises', sa.Column('image', sa.String, unique=False, index=True, default="empty"))



def downgrade() -> None:
    pass
