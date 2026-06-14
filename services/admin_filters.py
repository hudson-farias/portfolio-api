from typing import Optional

from sqlalchemy.orm import selectinload

from database.roles import RolesORM
from database.experiences import ExperiencesORM
from database.skills import SkillsORM
from database.social_networks import SocialNetworksORM
from database.tools import ToolsORM
from database.languages import LanguagesORM
from database.frameworks import FrameworksORM
from database.databases import DatabasesORM


def _exact_filters(**kwargs):
    return {key: value for key, value in kwargs.items() if value is not None}


async def filter_roles(is_auth: bool, q: Optional[str] = None, locale: Optional[str] = None, seniority: Optional[str] = None, show: Optional[bool] = None, active: Optional[bool] = None, featured: Optional[bool] = None):
    filters = _exact_filters(
        seniority = seniority,
        show = show,
        featured = featured,
    )

    if locale == 'none':
        filters['locale'] = None
    elif locale:
        filters['locale'] = locale

    if not is_auth:
        filters['active'] = True
    elif active is not None:
        filters['active'] = active

    async with RolesORM() as orm:
        roles = await orm.find_filtered(
            q = q.strip() if q else None,
            q_columns = ['title', 'summary', 'category'],
            **filters,
        )

    roles.sort(key = lambda role: (role.sort_order, role.id))
    return roles


async def filter_experiences(is_auth: bool, q: Optional[str] = None, role_id: Optional[int] = None, contract_type: Optional[str] = None, hidden: Optional[bool] = None):
    filters = _exact_filters(
        role_id = role_id,
        contract_type = contract_type,
    )

    if not is_auth:
        filters['hidden'] = False
    elif hidden is not None:
        filters['hidden'] = hidden

    async with ExperiencesORM() as orm:
        return await orm.find_filtered(
            options = selectinload(ExperiencesORM.role),
            q = q.strip() if q else None,
            q_columns = ['company', 'period', 'description'],
            **filters,
        )


async def filter_skills(q: Optional[str] = None):
    async with SkillsORM() as orm:
        return await orm.find_filtered(
            q = q.strip() if q else None,
            q_columns = ['name', 'icon'],
        )


async def filter_social_networks(q: Optional[str] = None, position: Optional[str] = None):
    array_contains = {'positions': position} if position else None

    async with SocialNetworksORM() as orm:
        return await orm.find_filtered(
            q = q.strip() if q else None,
            q_columns = ['url', 'icon'],
            array_contains = array_contains,
        )


async def filter_tools(q: Optional[str] = None):
    async with ToolsORM() as orm:
        tools = await orm.find_filtered(
            q = q.strip() if q else None,
            q_columns = ['name', 'icon', 'url'],
        )

    tools.sort(key = lambda tool: (tool.sort_order, tool.id))
    return tools


async def filter_languages(q: Optional[str] = None):
    async with LanguagesORM() as orm:
        languages = await orm.find_filtered(
            q = q.strip() if q else None,
            q_columns = ['name', 'icon'],
        )

    languages.sort(key = lambda language: (language.sort_order, language.id))
    return languages


async def filter_frameworks(q: Optional[str] = None):
    async with FrameworksORM() as orm:
        frameworks = await orm.find_filtered(
            q = q.strip() if q else None,
            q_columns = ['name', 'icon', 'scope'],
        )

    frameworks.sort(key = lambda framework: (framework.sort_order, framework.id))
    return frameworks


async def filter_databases(q: Optional[str] = None):
    async with DatabasesORM() as orm:
        databases = await orm.find_filtered(
            q = q.strip() if q else None,
            q_columns = ['name', 'icon', 'scope'],
        )

    databases.sort(key = lambda database: (database.sort_order, database.id))
    return databases
