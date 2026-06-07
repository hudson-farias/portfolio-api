from fastapi import Depends

from routers.admin import router, partial_authenticated

from database.experiences import ExperiencesORM
from database.skills import SkillsORM
from database.skills_categories import SkillsCategoriesORM
from database.projects import ProjectsORM
from database.social_networks import SocialNetworksORM

from models.admin.dashboard import *

from services.github import github
from services.experiences import roles_map, role_title


PREVIEW_EXPERIENCES = 3
PREVIEW_PROJECTS = 3
PREVIEW_SKILLS = 3
PREVIEW_SOCIAL = 3


@router.get('', status_code = 200, response_model = DashboardResponse)
async def get_dashboard(is_auth: bool = Depends(partial_authenticated)):
    data = DashboardResponse(counts = DashboardCounts(experiences = 0, skills = 0, projects = 0, social_networks = 0))

    titles = await roles_map()

    async with ExperiencesORM() as orm:
        if is_auth: experiences = await orm.find_many()
        else: experiences = await orm.find_many(hidden = False)

    data.counts.experiences = len(experiences)
    data.experiences = [
        DashboardExperience(
            id = experience.id,
            company = experience.company,
            period = experience.period,
            role = role_title(experience.role_id, titles) or '—',
            description = experience.description,
            hidden = experience.hidden,
        )
        for experience in experiences[:PREVIEW_EXPERIENCES]
    ]

    async with SkillsORM() as orm: skills = await orm.find_many()
    async with SkillsCategoriesORM() as orm: categories = await orm.find_many()

    data.counts.skills = len(skills)

    for category in categories:
        category_skills = [skill for skill in skills if skill.skill_category_id == category.id]
        data.skills.append(DashboardSkillCategory(
            title = category.title,
            skills = [DashboardSkill(id = skill.id, name = skill.name, icon = skill.icon) for skill in category_skills[:PREVIEW_SKILLS]],
        ))

    async with ProjectsORM() as orm: db_projects = await orm.find_many()
    projects_ids = [project.git_id for project in db_projects]

    visible = []

    for project in github(is_auth):
        if project['id'] not in projects_ids: continue

        visible.append(DashboardProject(
            id = project['id'],
            name = project['name'].replace('-', ' ').title(),
            html_url = project['html_url'],
            homepage = project.get('homepage'),
            description = project.get('description') or '',
        ))

    data.counts.projects = len(visible)
    data.projects = visible[:PREVIEW_PROJECTS]

    async with SocialNetworksORM() as orm: social_networks = await orm.find_many()

    data.counts.social_networks = len(social_networks)
    data.social_networks = [
        DashboardSocialNetwork(**item.dict())
        for item in social_networks[:PREVIEW_SOCIAL]
    ]

    return data
