from typing import Optional

from sqlalchemy.orm import selectinload

from database.roles import RolesORM
from database.experiences import ExperiencesORM
from database.skills import SkillsORM
from database.skills_categories import SkillsCategoriesORM
from database.social_networks import SocialNetworksORM


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


async def filter_skills(q: Optional[str] = None, skill_category_id: Optional[int] = None):
    filters = _exact_filters(skill_category_id = skill_category_id)

    async with SkillsORM() as orm:
        skills = await orm.find_filtered(
            q = q.strip() if q else None,
            q_columns = ['name', 'icon'],
            **filters,
        )

    async with SkillsCategoriesORM() as orm:
        categories = await orm.find_many()

    return skills, categories


async def filter_social_networks(q: Optional[str] = None, position: Optional[str] = None):
    array_contains = {'positions': position} if position else None

    async with SocialNetworksORM() as orm:
        return await orm.find_filtered(
            q = q.strip() if q else None,
            q_columns = ['url', 'icon'],
            array_contains = array_contains,
        )
