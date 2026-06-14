"""Create languages and frameworks tables

Revision ID: h4c5d6e7f8a9
Revises: g3b4c5d6e7f8
Create Date: 2026-06-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'h4c5d6e7f8a9'
down_revision: Union[str, None] = 'g3b4c5d6e7f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'languages',
        sa.Column('id', sa.Integer(), primary_key = True, autoincrement = True),
        sa.Column('name', sa.String(255), nullable = False),
        sa.Column('icon', sa.String(100), nullable = False),
        sa.Column('sort_order', sa.Integer(), nullable = False, server_default = '0'),
    )

    op.create_table(
        'frameworks',
        sa.Column('id', sa.Integer(), primary_key = True, autoincrement = True),
        sa.Column('name', sa.String(255), nullable = False),
        sa.Column('icon', sa.String(100), nullable = False),
        sa.Column('scope', sa.String(50), nullable = True),
        sa.Column('sort_order', sa.Integer(), nullable = False, server_default = '0'),
    )

    op.create_table(
        'language_frameworks',
        sa.Column('language_id', sa.Integer(), sa.ForeignKey('languages.id', ondelete = 'CASCADE'), nullable = False),
        sa.Column('framework_id', sa.Integer(), sa.ForeignKey('frameworks.id', ondelete = 'CASCADE'), nullable = False),
        sa.PrimaryKeyConstraint('language_id', 'framework_id'),
    )


def downgrade() -> None:
    op.drop_table('language_frameworks')
    op.drop_table('frameworks')
    op.drop_table('languages')
