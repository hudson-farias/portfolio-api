"""Rename profiles to profile and add contact columns

Revision ID: d0e1f2a3b4c5
Revises: c9d0e1f2a3b4
Create Date: 2026-06-14 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd0e1f2a3b4c5'
down_revision: Union[str, None] = 'c9d0e1f2a3b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('profiles', 'profile')

    op.add_column('profile', sa.Column('email', sa.String(255), nullable = True))
    op.add_column('profile', sa.Column('whatsapp', sa.String(30), nullable = True))
    op.add_column('profile', sa.Column('linkedin', sa.String(200), nullable = True))
    op.add_column('profile', sa.Column('github', sa.String(200), nullable = True))
    op.add_column('profile', sa.Column('gitlab', sa.String(200), nullable = True))


def downgrade() -> None:
    op.drop_column('profile', 'gitlab')
    op.drop_column('profile', 'github')
    op.drop_column('profile', 'linkedin')
    op.drop_column('profile', 'whatsapp')
    op.drop_column('profile', 'email')

    op.rename_table('profile', 'profiles')
