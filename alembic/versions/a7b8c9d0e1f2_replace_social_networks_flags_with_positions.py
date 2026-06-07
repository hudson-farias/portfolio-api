"""Replace social_networks show flags with positions array

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-06-07 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'a7b8c9d0e1f2'
down_revision: Union[str, None] = 'f6a7b8c9d0e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'social_networks',
        sa.Column(
            'positions',
            postgresql.ARRAY(sa.String()),
            nullable = False,
            server_default = '{}',
        ),
    )

    op.execute("""
        UPDATE social_networks
        SET positions = ARRAY_REMOVE(ARRAY[
            CASE WHEN show_header THEN 'about' END,
            CASE WHEN show_footer THEN 'footer' END
        ], NULL)
    """)

    op.drop_column('social_networks', 'show_header')
    op.drop_column('social_networks', 'show_footer')


def downgrade() -> None:
    op.add_column(
        'social_networks',
        sa.Column('show_header', sa.Boolean(), nullable = False, server_default = 'false'),
    )
    op.add_column(
        'social_networks',
        sa.Column('show_footer', sa.Boolean(), nullable = False, server_default = 'false'),
    )

    op.execute("""
        UPDATE social_networks
        SET
            show_header = 'about' = ANY(positions),
            show_footer = 'footer' = ANY(positions)
    """)

    op.drop_column('social_networks', 'positions')
