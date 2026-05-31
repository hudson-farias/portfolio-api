from fastapi import APIRouter
from asyncio import gather

from database.skills_categories import SkillsCategoriesORM
from database.skills import SkillsORM
from database.experiences import ExperiencesORM
from database.projects import ProjectsORM

from models import *

from services.github import github


router = APIRouter()


async def get_skills():
    data = []

    async with SkillsCategoriesORM() as orm: skills_categories = await orm.find_many()
    async with SkillsORM() as orm:
        for category in skills_categories:
            skills = await orm.find_many(skill_category_id = category.id)

            skill_data = Skills(title = category.title)
            skill_data.skills = [Skill(**skill.dict()) for skill in skills]

            data.append(skill_data)

    return data


async def get_experiences():
    async with ExperiencesORM() as orm: experiences = await orm.find_many()
    return [Experience(**experience.dict()) for experience in experiences]


async def get_projects():
    async with ProjectsORM() as orm: projects = await orm.find_many()
    projects_ids = [project.git_id for project in projects]

    projects = github(True)

    data = []

    for project in projects:
        project_dto = Project(**project)
        project_dto.name = project_dto.name.replace('-', ' ').title()
        project_dto.html_url = None if project['private'] else project_dto.html_url

        if project['id'] in projects_ids: data.append(project_dto)

    return data



@router.get('/', status_code = 200, response_model = ModelResponse)
async def get():
    data = ModelResponse()
    data.skills, data.experiences, data.projects = await gather(
        get_skills(),
        get_experiences(),
        get_projects(),
    )

    return data
