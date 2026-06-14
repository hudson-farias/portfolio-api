"""Remove skill categories

Revision ID: j6e7f8a9b0c1
Revises: i5d6e7f8a9b0
Create Date: 2026-06-15 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'j6e7f8a9b0c1'
down_revision: Union[str, None] = 'i5d6e7f8a9b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('skills_skill_category_id_fkey', 'skills', type_ = 'foreignkey')
    op.drop_column('skills', 'skill_category_id')
    op.drop_table('skills_categories')


def downgrade() -> None:
    op.create_table(
        'skills_categories',
        sa.Column('id', sa.Integer(), primary_key = True, autoincrement = True),
        sa.Column('title', sa.String(255), nullable = False),
    )

    op.add_column('skills', sa.Column('skill_category_id', sa.Integer(), nullable = True))
    op.execute("INSERT INTO skills_categories (title) VALUES ('Softskills')")
    op.execute('UPDATE skills SET skill_category_id = (SELECT id FROM skills_categories WHERE title = \'Softskills\' LIMIT 1)')
    op.alter_column('skills', 'skill_category_id', nullable = False)
    op.create_foreign_key('skills_skill_category_id_fkey', 'skills', 'skills_categories', ['skill_category_id'], ['id'])
