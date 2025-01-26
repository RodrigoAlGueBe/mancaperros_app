"""create user_tracker table

Revision ID: 9cfbf8dd7525
Revises: de1efaa5a6ec
Create Date: 2024-11-21 12:36:34.536183

"""
from alembic import op
import sqlalchemy as sa

from datetime import date


# revision identifiers, used by Alembic.
revision = '9cfbf8dd7525'
down_revision = 'de1efaa5a6ec'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users_tracker', 
            sa.Column('user_tracker_id', sa.Integer(), nullable=False, primary_key=True, index=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.user_id'), nullable=False),
            sa.Column('record_datetime', sa.DateTime(), nullable=False, unique=False, index=True, default=date.today()),
            sa.Column('info_type', sa.String(), nullable=False, unique=False, index=True, default="Non_specifed"),
            sa.Column('info_description', sa.String(), nullable=True, unique=False, index=True, default="Non_specifed"),
            sa.Column('exercise_increments', sa.JSON(), nullable=True, unique=False, default=None),
            sa.Column('push_increment', sa.Integer(), nullable=False, unique=False, default=0),
            sa.Column('pull_increment', sa.Integer(), nullable=False, unique=False, default=0),
            sa.Column('isometric_increment', sa.Integer, nullable=False, unique=False, default=0),
            sa.Column('push_increment_units', sa.String, nullable=False, unique=False, default="uds")
            )


def downgrade() -> None:
    op.drop_table('users_tracker')
