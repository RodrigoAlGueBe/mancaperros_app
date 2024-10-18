"""Add cascade delete to Exercise plans and Rutines ONLY IN SQLITE

Revision ID: 0f0ae0bbb5c9
Revises: bcc1303c427a
Create Date: 2024-09-30 23:30:08.804773

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


# revision identifiers, used by Alembic.
revision = '0f0ae0bbb5c9'
down_revision = 'bcc1303c427a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'exercise_plans_new',
        sa.Column('exercise_plan_id', sa.Integer, primary_key=True, index=True),
        sa.Column('exercise_plan_name', sa.String(50), nullable=True, unique=False, index=True, default="New exercise plan"),
        sa.Column('exercise_plan_type', sa.String, nullable=True, unique=False, index=True, default="New exercise plan type"),
        sa.Column('difficult_level', sa.String, nullable=True, unique=False, index=True, default="New exercise plan difficult level"),
        sa.Column('creation_date', sa.Date, nullable=True, unique=False, index=True, default="1970-01-01"),
        sa.Column('user_owner_id', sa.Integer, sa.ForeignKey('users.user_id'), nullable=True)
    )

    op.create_table(
        'rutines_new',
        sa.Column('rutine_id', sa.Integer, primary_key=True, index=True),
        sa.Column('rutine_type', sa.String, nullable=True, unique=False, index=True, default="New rutine type"),
        sa.Column('rutine_name', sa.String(50), nullable=True, unique=False, index=True, default="New rutine name"),
        sa.Column('rutine_group', sa.String, nullable=True, unique=False, index=True, default="New rutine group"),
        sa.Column('rutine_category', sa.String, nullable=True, unique=False, index=True, default="New rutine category"),
        sa.Column('exercise_plan_id', sa.Integer, sa.ForeignKey('exercise_plans.exercise_plan_id'), nullable=True),
        sa.Column('rounds', sa.Integer, nullable=True, unique=False, index=True, default=0),
        sa.Column('rst_btw_exercises', sa.String, unique=False, index=True, default="0"),
        sa.Column('rst_btw_rounds', sa.String, unique=False, index=True, default="0"),
        sa.Column('difficult_level', sa.String, unique=False, index=True, default="New rutine difficult level")
    )

    op.create_table(
        'exercises_new',
        sa.Column('exercise_id', sa.Integer, primary_key=True, index=True, unique=True),
        sa.Column('exercise_name', sa.String(50), nullable=False, unique=False, index=True, default="New exercise name"),
        sa.Column('rep', sa.String(50), nullable=False, unique=False, index=True, default="empty"),
        sa.Column('exercise_type', sa.String(50), nullable=False, unique=False, index=True, default="New exercise type"),
        sa.Column('exercise_group', sa.String(50), nullable=False, unique=False, index=True, default="New exercise group"),
        sa.Column('rutine_id', sa.Integer, sa.ForeignKey('rutines.rutine_id'), nullable=False),
        sa.Column('image', sa.String, unique=False, index=True, default="empty")
    )

    op.create_table(
        'exercise_plans_global_new',
        sa.Column('exercise_plan_id', sa.Integer, primary_key=True, index=True),
        sa.Column('exercise_plan_name', sa.String, nullable=False, unique=False, index=True, default="New exercise plan"),
        sa.Column('user_creator_id', sa.Integer, sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('exercise_plan_type', sa.String, nullable=False, unique=False, index=True, default="New exercise plan type"),
        sa.Column('creation_date', sa.Date, nullable=False, unique=False, index=True, default="1970-01-01"),
        sa.Column('difficult_level', sa.String, nullable=False, unique=False, index=True, default="New exercise plan difficult level")
    )

    op.create_table(
        'rutines_global_new',
        sa.Column('rutine_id', sa.Integer, primary_key=True, index=True),
        sa.Column('rutine_type', sa.String, nullable=False, unique=False, index=True, default="New rutine type"),
        sa.Column('rutine_name', sa.String(50), nullable=False, unique=False, index=True, default="New rutine name"),
        sa.Column('rutine_group', sa.String, nullable=False, unique=False, index=True, default="New rutine group"),
        sa.Column('rutine_category', sa.String, nullable=False, unique=False, index=True, default="New rutine category"),
        sa.Column('exercise_plan_id', sa.Integer, sa.ForeignKey('exercise_plans_global.exercise_plan_id'), nullable=False),
        sa.Column('rounds', sa.Integer, nullable=False, unique=False, index=True, default=0),
        sa.Column('rst_btw_exercises', sa.String, unique=False, index=True, default="0"),
        sa.Column('rst_btw_rounds', sa.String, unique=False, index=True, default="0"),
        sa.Column('difficult_level', sa.String, unique=False, index=True, default="New rutine difficult level")
    )

    op.create_table(
        'exercises_global_new',
        sa.Column('exercise_id', sa.Integer, primary_key=True, index=True, unique=True),
        sa.Column('exercise_name', sa.String(50), nullable=False, unique=False, index=True, default="New exercise name"),
        sa.Column('rep', sa.String(50), nullable=False, unique=False, index=True, default="empty"),
        sa.Column('exercise_type', sa.String(50), nullable=False, unique=False, index=True, default="New exercise type"),
        sa.Column('exercise_group', sa.String(50), nullable=False, unique=False, index=True, default="New exercise group"),
        sa.Column('rutine_id', sa.Integer, sa.ForeignKey('rutines_global.rutine_id'), nullable=False),
        sa.Column('image', sa.String, unique=False, index=True, default="empty")
    )

    
    # Copiar los datos de la tabla antigua a la nueva
    op.execute('''
        INSERT INTO exercise_plans_new (exercise_plan_id, exercise_plan_name, exercise_plan_type, difficult_level, creation_date, user_owner_id)
        SELECT exercise_plan_id, exercise_plan_name, exercise_plan_type, difficult_level, creation_date, user_owner_id
        FROM exercise_plans
    ''')

    op.execute('''
        INSERT INTO rutines_new (rutine_id, rutine_type, rutine_name, rutine_group, rutine_category, exercise_plan_id, rounds, rst_btw_exercises, rst_btw_rounds, difficult_level)
        SELECT rutine_id, rutine_type, rutine_name, rutine_group, rutine_category, exercise_plan_id, rounds, rst_btw_exercises, rst_btw_rounds, difficult_level
        FROM rutines
    ''')

    op.execute('''
        INSERT INTO exercises_new (exercise_id, exercise_name, rep, exercise_type, exercise_group, rutine_id, image)
        SELECT exercise_id, exercise_name, rep, exercise_type, exercise_group, rutine_id, image
        FROM exercises
    ''')

    op.execute('''
        INSERT INTO exercise_plans_global_new (exercise_plan_id, exercise_plan_name, user_creator_id, exercise_plan_type, creation_date, difficult_level)
        SELECT exercise_plan_id, exercise_plan_name, user_creator_id, exercise_plan_type, creation_date, difficult_level
        FROM exercise_plans_global
    ''')

    op.execute('''
        INSERT INTO rutines_global_new (rutine_id, rutine_type, rutine_name, rutine_group, rutine_category, exercise_plan_id, rounds, rst_btw_exercises, rst_btw_rounds, difficult_level)
        SELECT rutine_id, rutine_type, rutine_name, rutine_group, rutine_category, exercise_plan_id, rounds, rst_btw_exercises, rst_btw_rounds, difficult_level
        FROM rutines_global
    ''')

    op.execute('''
        INSERT INTO exercises_global_new (exercise_id, exercise_name, rep, exercise_type, exercise_group, rutine_id, image)
        SELECT exercise_id, exercise_name, rep, exercise_type, exercise_group, rutine_id, image
        FROM exercises_global
    ''')
    
    # Eliminar la tabla antigua
    op.drop_table('exercise_plans')
    op.drop_table('rutines')
    op.drop_table('exercises')
    op.drop_table('exercise_plans_global')
    op.drop_table('rutines_global')
    op.drop_table('exercises_global')
    
    # Renombrar la nueva tabla a la antigua
    op.rename_table('exercise_plans_new', 'exercise_plans')
    op.rename_table('rutines_new', 'rutines')
    op.rename_table('exercises_new', 'exercises')
    op.rename_table('exercise_plans_global_new', 'exercise_plans_global')
    op.rename_table('rutines_global_new', 'rutines_global')
    op.rename_table('exercises_global_new', 'exercises_global')

def downgrade():
    pass