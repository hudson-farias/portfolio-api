"""Make projects.live_url nullable

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-06-14 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b8c9d0e1f2a3'
down_revision: Union[str, None] = 'a7b8c9d0e1f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'projects',
        'live_url',
        existing_type = sa.String(150),
        nullable = True,
    )


def downgrade() -> None:
    op.alter_column(
        'projects',
        'live_url',
        existing_type = sa.String(150),
        nullable = False,
    )
