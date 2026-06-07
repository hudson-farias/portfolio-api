"""Create profiles table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'profiles',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('about_me', sa.Text(), nullable=False),
        sa.Column('roles', sa.ARRAY(sa.String(150)), nullable=False, server_default='{}'),
    )


def downgrade() -> None:
    op.drop_table('profiles')
