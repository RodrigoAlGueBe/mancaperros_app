"""Erase the table users_tracker

Revision ID: de1efaa5a6ec
Revises: 0f0ae0bbb5c9
Create Date: 2024-11-21 11:56:49.041130

"""
from alembic import op
import sqlalchemy as sa

from datetime import date


# revision identifiers, used by Alembic.
revision = 'de1efaa5a6ec'
down_revision = '0f0ae0bbb5c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users_tracker')

    # ### end Alembic commands ###
