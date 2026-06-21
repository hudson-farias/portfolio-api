"""Create translation tables and roles visible_locales

Revision ID: l8m9n0o1p2q3
Revises: k7f8a9b0c1d2
Create Date: 2026-06-21 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'l8m9n0o1p2q3'
down_revision: Union[str, None] = 'k7f8a9b0c1d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'profile_translations',
        sa.Column('id', sa.Integer(), primary_key = True, autoincrement = True),
        sa.Column('profile_id', sa.Integer(), sa.ForeignKey('profile.id', ondelete = 'CASCADE'), nullable = False),
        sa.Column('locale', sa.String(2), nullable = False),
        sa.Column('summary', sa.Text(), nullable = False, server_default = ''),
        sa.Column('about_me', sa.Text(), nullable = False, server_default = ''),
        sa.Column('location', sa.String(150), nullable = False, server_default = ''),
        sa.UniqueConstraint('profile_id', 'locale', name = 'uq_profile_translations_profile_locale'),
    )

    op.create_table(
        'experience_translations',
        sa.Column('id', sa.Integer(), primary_key = True, autoincrement = True),
        sa.Column('experience_id', sa.Integer(), sa.ForeignKey('experiences.id', ondelete = 'CASCADE'), nullable = False),
        sa.Column('locale', sa.String(2), nullable = False),
        sa.Column('period', sa.String(100), nullable = False, server_default = ''),
        sa.Column('description', sa.Text(), nullable = False, server_default = ''),
        sa.UniqueConstraint('experience_id', 'locale', name = 'uq_experience_translations_experience_locale'),
    )

    op.create_table(
        'project_translations',
        sa.Column('id', sa.Integer(), primary_key = True, autoincrement = True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id', ondelete = 'CASCADE'), nullable = False),
        sa.Column('locale', sa.String(2), nullable = False),
        sa.Column('title', sa.String(255), nullable = False, server_default = ''),
        sa.Column('description', sa.Text(), nullable = True),
        sa.UniqueConstraint('project_id', 'locale', name = 'uq_project_translations_project_locale'),
    )

    op.create_table(
        'role_translations',
        sa.Column('id', sa.Integer(), primary_key = True, autoincrement = True),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id', ondelete = 'CASCADE'), nullable = False),
        sa.Column('locale', sa.String(2), nullable = False),
        sa.Column('title', sa.String(150), nullable = False, server_default = ''),
        sa.Column('summary', sa.Text(), nullable = True),
        sa.UniqueConstraint('role_id', 'locale', name = 'uq_role_translations_role_locale'),
    )

    op.add_column('roles', sa.Column('visible_locales', postgresql.ARRAY(sa.String(2)), nullable = True))

    op.execute("""
        INSERT INTO profile_translations (profile_id, locale, summary, about_me, location)
        SELECT id, 'pt', summary, about_me, COALESCE(location, '')
        FROM profile
    """)

    op.execute("""
        INSERT INTO experience_translations (experience_id, locale, period, description)
        SELECT id, 'pt', period, description
        FROM experiences
    """)

    op.execute("""
        INSERT INTO project_translations (project_id, locale, title, description)
        SELECT id, 'pt', COALESCE(title, ''), description
        FROM projects
    """)

    op.execute("""
        INSERT INTO role_translations (role_id, locale, title, summary)
        SELECT id, COALESCE(locale, 'pt'), title, summary
        FROM roles
    """)

    op.execute("""
        UPDATE roles
        SET visible_locales = CASE
            WHEN locale IS NULL THEN NULL
            WHEN locale = 'pt' THEN ARRAY['pt']::varchar(2)[]
            WHEN locale = 'en' THEN ARRAY['en']::varchar(2)[]
            ELSE ARRAY[locale]::varchar(2)[]
        END
    """)


def downgrade() -> None:
    op.drop_column('roles', 'visible_locales')
    op.drop_table('role_translations')
    op.drop_table('project_translations')
    op.drop_table('experience_translations')
    op.drop_table('profile_translations')
