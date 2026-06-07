"""Add role metadata columns

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-06-07 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('roles_title_key', 'roles', type_='unique')

    op.add_column('roles', sa.Column('summary', sa.Text(), nullable=True))
    op.add_column('roles', sa.Column('category', sa.String(100), nullable=True))
    op.add_column('roles', sa.Column('seniority', sa.String(50), nullable=True))
    op.add_column('roles', sa.Column('featured', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('roles', sa.Column('locale', sa.String(10), nullable=False, server_default='pt'))
    op.add_column('roles', sa.Column('active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('roles', sa.Column('color', sa.String(20), nullable=True))
    op.add_column('roles', sa.Column('icon', sa.String(100), nullable=True))

    op.create_unique_constraint('uq_roles_title_locale', 'roles', ['title', 'locale'])

    op.create_check_constraint(
        'ck_roles_seniority',
        'roles',
        "seniority IS NULL OR seniority IN ('Junior', 'Pleno', 'Senior', 'Lead')",
    )

def downgrade() -> None:
    op.drop_constraint('ck_roles_seniority', 'roles', type_='check')
    op.drop_constraint('uq_roles_title_locale', 'roles', type_='unique')

    op.drop_column('roles', 'icon')
    op.drop_column('roles', 'color')
    op.drop_column('roles', 'active')
    op.drop_column('roles', 'locale')
    op.drop_column('roles', 'featured')
    op.drop_column('roles', 'seniority')
    op.drop_column('roles', 'category')
    op.drop_column('roles', 'summary')

    op.create_unique_constraint('roles_title_key', 'roles', ['title'])
