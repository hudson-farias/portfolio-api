"""Drop roles visible_locales column

Revision ID: n0o1p2q3r4s5
Revises: m9n0o1p2q3r4
Create Date: 2026-06-21 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'n0o1p2q3r4s5'
down_revision: Union[str, None] = 'm9n0o1p2q3r4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('roles', 'visible_locales')


def downgrade() -> None:
    op.add_column('roles', sa.Column('visible_locales', postgresql.ARRAY(sa.String(2)), nullable = True))

    op.execute("""
        UPDATE roles r SET visible_locales = ARRAY[t.locale]::varchar(2)[]
        FROM role_translations t
        WHERE t.role_id = r.id AND t.locale IN ('pt', 'en')
    """)
