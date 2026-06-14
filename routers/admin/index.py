from fastapi import Depends

from sqlalchemy.orm import selectinload

from routers.admin import router, partial_authenticated

from database.experiences import ExperiencesORM
from database.skills import SkillsORM
from database.projects import ProjectsORM
from database.social_networks import SocialNetworksORM
from database.tools import ToolsORM
from database.languages import LanguagesORM
from database.frameworks import FrameworksORM
from database.databases import DatabasesORM

from models.admin.dashboard import *

from services.github import github


PREVIEW_EXPERIENCES = 3
PREVIEW_PROJECTS = 3
PREVIEW_SKILLS = 3
PREVIEW_SOCIAL = 3
PREVIEW_TOOLS = 3
PREVIEW_LANGUAGES = 3
PREVIEW_FRAMEWORKS = 3
PREVIEW_DATABASES = 3


@router.get('', status_code = 200, response_model = DashboardResponse)
async def get_dashboard(is_auth: bool = Depends(partial_authenticated)):
    data = DashboardResponse(counts = DashboardCounts(experiences = 0, skills = 0, projects = 0, social_networks = 0, tools = 0, languages = 0, frameworks = 0, databases = 0))

    async with ExperiencesORM() as orm:
        options = selectinload(ExperiencesORM.role)
        if is_auth: experiences = await orm.find_many(options = options)
        else: experiences = await orm.find_many(hidden = False, options = options)

    data.counts.experiences = len(experiences)
    data.experiences = [
        DashboardExperience(
            id = experience.id,
            company = experience.company,
            period = experience.period,
            role = experience.role_title or '—',
            description = experience.description,
            hidden = experience.hidden,
        )
        for experience in experiences[:PREVIEW_EXPERIENCES]
    ]

    async with SkillsORM() as orm: skills = await orm.find_many()

    data.counts.skills = len(skills)
    data.skills = [
        DashboardSkill(id = skill.id, name = skill.name, icon = skill.icon)
        for skill in skills[:PREVIEW_SKILLS]
    ]

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

    async with ToolsORM() as orm: tools = await orm.find_many()
    tools.sort(key = lambda tool: (tool.sort_order, tool.id))

    data.counts.tools = len(tools)
    data.tools = [
        DashboardTool(**item.dict())
        for item in tools[:PREVIEW_TOOLS]
    ]

    async with LanguagesORM() as orm: languages = await orm.find_many()
    languages.sort(key = lambda language: (language.sort_order, language.id))

    data.counts.languages = len(languages)
    data.languages = [
        DashboardLanguage(**item.dict())
        for item in languages[:PREVIEW_LANGUAGES]
    ]

    async with FrameworksORM() as orm: frameworks = await orm.find_many()
    frameworks.sort(key = lambda framework: (framework.sort_order, framework.id))

    data.counts.frameworks = len(frameworks)
    data.frameworks = [
        DashboardFramework(**item.dict())
        for item in frameworks[:PREVIEW_FRAMEWORKS]
    ]

    async with DatabasesORM() as orm: databases = await orm.find_many()
    databases.sort(key = lambda database: (database.sort_order, database.id))

    data.counts.databases = len(databases)
    data.databases = [
        DashboardDatabase(**item.dict())
        for item in databases[:PREVIEW_DATABASES]
    ]

    return data
