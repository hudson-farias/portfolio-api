"""Create roles table and refactor experiences

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-06-07 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('title', sa.String(150), nullable=False, unique=True),
        sa.Column('show', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
    )

    op.execute("""
        INSERT INTO roles (title, show, sort_order)
        SELECT DISTINCT role, false, 0
        FROM experiences
        WHERE role IS NOT NULL AND role <> ''
        ON CONFLICT (title) DO NOTHING
    """)

    op.execute("""
        INSERT INTO roles (title, show, sort_order)
        SELECT DISTINCT unnest(roles), true, 0
        FROM profiles
        WHERE roles IS NOT NULL
        ON CONFLICT (title) DO UPDATE SET show = true
    """)

    op.add_column('experiences', sa.Column('role_id', sa.Integer(), nullable=True))
    op.add_column('experiences', sa.Column('contract_type', sa.String(20), nullable=True))

    op.execute("""
        UPDATE experiences e
        SET role_id = r.id
        FROM roles r
        WHERE e.role = r.title
    """)

    op.create_foreign_key(
        'fk_experiences_role_id',
        'experiences',
        'roles',
        ['role_id'],
        ['id'],
        ondelete='SET NULL',
    )

    op.create_check_constraint(
        'ck_experiences_contract_type',
        'experiences',
        "contract_type IS NULL OR contract_type IN ('CLT', 'PJ', 'FREELANCER')",
    )

    op.drop_column('experiences', 'role')
    op.drop_column('profiles', 'roles')


def downgrade() -> None:
    op.add_column('profiles', sa.Column('roles', sa.ARRAY(sa.String(150)), nullable=False, server_default='{}'))
    op.add_column('experiences', sa.Column('role', sa.String(150), nullable=False, server_default=''))

    op.execute("""
        UPDATE experiences e
        SET role = r.title
        FROM roles r
        WHERE e.role_id = r.id
    """)

    op.drop_constraint('ck_experiences_contract_type', 'experiences', type_='check')
    op.drop_constraint('fk_experiences_role_id', 'experiences', type_='foreignkey')
    op.drop_column('experiences', 'contract_type')
    op.drop_column('experiences', 'role_id')
    op.drop_table('roles')
