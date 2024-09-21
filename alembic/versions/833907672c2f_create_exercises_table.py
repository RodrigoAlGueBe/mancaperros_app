"""create exercises table

Revision ID: 833907672c2f
Revises: c7db2124256e
Create Date: 2023-10-20 17:51:09.647753

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '833907672c2f'
down_revision = 'c7db2124256e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'exercises',
        sa.Column('exercise_id', sa.Integer, primary_key=True, index=True, unique=True),
        sa.Column('exercise_name', sa.String(50), nullable=False, unique=False, index=True, default="New exercise name"),
        sa.Column('rep', sa.String(50), nullable=False, unique=False, index=True, default="empty"),
        sa.Column('exercise_type', sa.String(50), nullable=False, unique=False, index=True, default="New exercise type"),
        sa.Column('exercise_group', sa.String(50), nullable=False, unique=False, index=True, default="New exercise group"),
        sa.Column('rutine_id', sa.Integer, sa.ForeignKey('rutines.rutine_id'), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("exercises")
