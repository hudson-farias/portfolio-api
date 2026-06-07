"""Make roles locale nullable and drop check constraint

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-06-07 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('ALTER TABLE roles DROP CONSTRAINT IF EXISTS ck_roles_locale')
    op.execute("UPDATE roles SET locale = NULL WHERE locale = 'todos'")
    op.alter_column(
        'roles',
        'locale',
        existing_type = sa.String(10),
        nullable = True,
        server_default = None,
    )


def downgrade() -> None:
    op.execute("UPDATE roles SET locale = 'pt' WHERE locale IS NULL")
    op.alter_column(
        'roles',
        'locale',
        existing_type = sa.String(10),
        nullable = False,
        server_default = 'pt',
    )
