from fastapi import Depends, HTTPException
from routers.admin import router, partial_authenticated, has_authenticated

from database.projects import ProjectsORM

from models.admin.projects import *

from services.github import github


def github_meta(project):
    return {
        'private': bool(project.get('private')),
        'language': project.get('language'),
        'stars': project.get('stargazers_count') or 0,
        'forks': project.get('forks_count') or 0,
        'updated_at': project.get('updated_at'),
        'archived': bool(project.get('archived')),
        'fork': bool(project.get('fork'))
    }


def external_project_dto(db):
    return Project(
        git_id = db.git_id,
        name = db.title or 'Projeto externo',
        html_url = db.repo_url or '',
        description = db.description,
        title = db.title,
        image_url = db.image_url,
        live_url = db.live_url,
        repo_url = db.repo_url,
        external = True,
    )


def github_repo_url(git_id: int):
    for project in github(True):
        if project['id'] != git_id: continue
        if project.get('private'): return None
        return project.get('html_url')


async def next_external_git_id(orm):
    projects = await orm.find_many()
    external_ids = [project.git_id for project in projects if project.git_id < 0]
    return min(external_ids + [0]) - 1


async def response_data(is_auth: bool):
    async with ProjectsORM() as orm: projects_db = await orm.find_many()
    projects_mapper = {project.git_id: project for project in projects_db if project.git_id > 0}
    projects_ids = set(projects_mapper.keys())

    projects = github(is_auth)

    data = Projects()

    for project in projects:
        git_id = project['id']
        name = project['name'].replace('-', ' ').title()
        homepage = project.get('homepage') or None
        description = project.get('description') or None

        project_dto = Project(
            git_id = git_id,
            name = name,
            html_url = project.get('html_url') or '',
            homepage = homepage,
            description = description,
            **github_meta(project),
        )

        if git_id in projects_ids:
            db = projects_mapper[git_id]
            project_dto.title = db.title
            project_dto.description = db.description or description
            project_dto.image_url = db.image_url
            project_dto.live_url = db.live_url
            project_dto.repo_url = db.repo_url
            data.visible.append(project_dto)

        else: data.options.append(project_dto)

    for db in projects_db:
        if db.git_id < 0: data.visible.append(external_project_dto(db))

    return data


@router.get('/projects', status_code = 200, response_model = Projects)
async def get_projects(is_auth: bool = Depends(partial_authenticated)):
    return await response_data(is_auth)



@router.post('/projects/external', status_code = 201)
async def post_external_project(params: ProjectPayload, is_auth: bool = Depends(has_authenticated)):
    if not params.repo_url: raise HTTPException(status_code = 422, detail = 'repo_url é obrigatório para projetos externos')

    data = params.dict()

    async with ProjectsORM() as orm:
        git_id = await next_external_git_id(orm)
        await orm.create(git_id = git_id, **data)

    return await response_data(is_auth)



@router.post('/projects/{git_id}', status_code = 201)
async def post_projects(git_id: int, params: ProjectPayload, is_auth: bool = Depends(has_authenticated)):
    data = params.dict()
    data['repo_url'] = github_repo_url(git_id)

    async with ProjectsORM() as orm:
        await orm.create(git_id = git_id, **data)

    return await response_data(is_auth)



@router.put('/projects/{git_id}', status_code = 201)
async def put_projects(git_id: int, params: ProjectPayload, is_auth: bool = Depends(has_authenticated)):
    data = params.dict()

    if git_id > 0: data['repo_url'] = github_repo_url(git_id)
    elif not data.get('repo_url'): raise HTTPException(status_code = 422, detail = 'repo_url é obrigatório para projetos externos')

    async with ProjectsORM() as orm:
        project = await orm.find_one(git_id = git_id)
        if project: await orm.update(id = project.id, **data)

    return await response_data(is_auth)



@router.delete('/projects/{git_id}', status_code = 201)
async def delete_project(git_id: int, is_auth: bool = Depends(has_authenticated)):
    async with ProjectsORM() as orm: await orm.delete(git_id = git_id)
    return await response_data(is_auth)
