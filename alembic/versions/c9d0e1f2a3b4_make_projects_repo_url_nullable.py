"""Make projects.repo_url nullable

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-06-14 12:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c9d0e1f2a3b4'
down_revision: Union[str, None] = 'b8c9d0e1f2a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'projects',
        'repo_url',
        existing_type = sa.String(150),
        nullable = True,
    )


def downgrade() -> None:
    op.alter_column(
        'projects',
        'repo_url',
        existing_type = sa.String(150),
        nullable = False,
    )
