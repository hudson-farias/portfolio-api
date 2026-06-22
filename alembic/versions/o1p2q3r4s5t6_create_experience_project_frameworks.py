"""Create experience_frameworks and project_frameworks tables

Revision ID: o1p2q3r4s5t6
Revises: n0o1p2q3r4s5
Create Date: 2026-06-21 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'o1p2q3r4s5t6'
down_revision: Union[str, None] = 'n0o1p2q3r4s5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'experience_frameworks',
        sa.Column('experience_id', sa.Integer(), nullable = False),
        sa.Column('framework_id', sa.Integer(), nullable = False),
        sa.ForeignKeyConstraint(['experience_id'], ['experiences.id'], ondelete = 'CASCADE'),
        sa.ForeignKeyConstraint(['framework_id'], ['frameworks.id'], ondelete = 'CASCADE'),
        sa.PrimaryKeyConstraint('experience_id', 'framework_id'),
    )

    op.create_table(
        'project_frameworks',
        sa.Column('project_id', sa.Integer(), nullable = False),
        sa.Column('framework_id', sa.Integer(), nullable = False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete = 'CASCADE'),
        sa.ForeignKeyConstraint(['framework_id'], ['frameworks.id'], ondelete = 'CASCADE'),
        sa.PrimaryKeyConstraint('project_id', 'framework_id'),
    )


def downgrade():
    op.drop_table('project_frameworks')
    op.drop_table('experience_frameworks')
