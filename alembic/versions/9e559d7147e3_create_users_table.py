"""create users table

Revision ID: 9e559d7147e3
Revises: 
Create Date: 2023-10-20 17:50:20.792935

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e559d7147e3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_name', sa.String(50), nullable=False, unique=False, index=True),
        sa.Column('hashed_password', sa.String(100), nullable=False, unique=False, index=True),
        sa.Column('email', sa.String(50), nullable=False, unique=True, index=True),
    )


def downgrade() -> None:
    op.drop_table('users')

