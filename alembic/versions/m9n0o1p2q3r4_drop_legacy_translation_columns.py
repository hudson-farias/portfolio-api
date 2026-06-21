"""Drop legacy translation columns

Revision ID: m9n0o1p2q3r4
Revises: l8m9n0o1p2q3
Create Date: 2026-06-21 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'm9n0o1p2q3r4'
down_revision: Union[str, None] = 'l8m9n0o1p2q3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('profile', 'summary')
    op.drop_column('profile', 'about_me')
    op.drop_column('profile', 'location')

    op.drop_column('experiences', 'period')
    op.drop_column('experiences', 'description')

    op.drop_column('projects', 'title')
    op.drop_column('projects', 'description')

    op.drop_column('roles', 'title')
    op.drop_column('roles', 'summary')
    op.drop_column('roles', 'locale')


def downgrade() -> None:
    op.add_column('roles', sa.Column('locale', sa.String(10), nullable = True, server_default = 'pt'))
    op.add_column('roles', sa.Column('summary', sa.Text(), nullable = True))
    op.add_column('roles', sa.Column('title', sa.String(150), nullable = False, server_default = ''))

    op.add_column('projects', sa.Column('description', sa.String(255), nullable = True))
    op.add_column('projects', sa.Column('title', sa.String(255), nullable = True))

    op.add_column('experiences', sa.Column('description', sa.String(255), nullable = False, server_default = ''))
    op.add_column('experiences', sa.Column('period', sa.String(100), nullable = False, server_default = ''))

    op.add_column('profile', sa.Column('location', sa.String(150), nullable = False, server_default = ''))
    op.add_column('profile', sa.Column('about_me', sa.Text(), nullable = False, server_default = ''))
    op.add_column('profile', sa.Column('summary', sa.Text(), nullable = False, server_default = ''))

    op.execute("""
        UPDATE profile p SET
            summary = t.summary,
            about_me = t.about_me,
            location = t.location
        FROM profile_translations t
        WHERE t.profile_id = p.id AND t.locale = 'pt'
    """)

    op.execute("""
        UPDATE experiences e SET
            period = t.period,
            description = t.description
        FROM experience_translations t
        WHERE t.experience_id = e.id AND t.locale = 'pt'
    """)

    op.execute("""
        UPDATE projects p SET
            title = t.title,
            description = t.description
        FROM project_translations t
        WHERE t.project_id = p.id AND t.locale = 'pt'
    """)

    op.execute("""
        UPDATE roles r SET
            title = t.title,
            summary = t.summary,
            locale = CASE
                WHEN r.visible_locales IS NULL THEN NULL
                WHEN r.visible_locales = ARRAY['pt']::varchar(2)[] THEN 'pt'
                WHEN r.visible_locales = ARRAY['en']::varchar(2)[] THEN 'en'
                ELSE r.visible_locales[1]
            END
        FROM role_translations t
        WHERE t.role_id = r.id AND t.locale = 'pt'
    """)
