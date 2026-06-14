"""Create databases table

Revision ID: i5d6e7f8a9b0
Revises: h4c5d6e7f8a9
Create Date: 2026-06-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'i5d6e7f8a9b0'
down_revision: Union[str, None] = 'h4c5d6e7f8a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'databases',
        sa.Column('id', sa.Integer(), primary_key = True, autoincrement = True),
        sa.Column('name', sa.String(255), nullable = False),
        sa.Column('icon', sa.String(100), nullable = False),
        sa.Column('scope', sa.String(50), nullable = True),
        sa.Column('sort_order', sa.Integer(), nullable = False, server_default = '0'),
    )


def downgrade() -> None:
    op.drop_table('databases')
