"""Add live_url to experiences

Revision ID: k7f8a9b0c1d2
Revises: j6e7f8a9b0c1
Create Date: 2026-06-21 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'k7f8a9b0c1d2'
down_revision: Union[str, None] = 'j6e7f8a9b0c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'experiences',
        sa.Column('live_url', sa.String(150), nullable = True),
    )


def downgrade() -> None:
    op.drop_column('experiences', 'live_url')
