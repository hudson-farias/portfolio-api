"""Make profile contact columns not null

Revision ID: e1f2a3b4c5d6
Revises: d0e1f2a3b4c5
Create Date: 2026-06-14 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e1f2a3b4c5d6'
down_revision: Union[str, None] = 'd0e1f2a3b4c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CONTACT_COLUMNS = (
    ('email', sa.String(255)),
    ('whatsapp', sa.String(30)),
    ('linkedin', sa.String(200)),
    ('github', sa.String(200)),
    ('gitlab', sa.String(200)),
)


def upgrade() -> None:
    for name, column_type in CONTACT_COLUMNS:
        op.alter_column(
            'profile',
            name,
            existing_type = column_type,
            nullable = False,
        )


def downgrade() -> None:
    for name, column_type in CONTACT_COLUMNS:
        op.alter_column(
            'profile',
            name,
            existing_type = column_type,
            nullable = True,
        )
