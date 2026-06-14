"""Create tools table

Revision ID: g3b4c5d6e7f8
Revises: f2a3b4c5d6e7
Create Date: 2026-06-14 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'g3b4c5d6e7f8'
down_revision: Union[str, None] = 'f2a3b4c5d6e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'tools',
        sa.Column('id', sa.Integer(), primary_key = True, autoincrement = True),
        sa.Column('name', sa.String(255), nullable = False),
        sa.Column('icon', sa.String(100), nullable = False),
        sa.Column('url', sa.String(255), nullable = True),
        sa.Column('sort_order', sa.Integer(), nullable = False, server_default = '0'),
    )


def downgrade() -> None:
    op.drop_table('tools')
