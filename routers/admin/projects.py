from fastapi import Depends, HTTPException
from routers.admin import router, partial_authenticated, has_authenticated

from database.projects import ProjectsORM
from database.project_translations import ProjectTranslationsORM
from database.project_frameworks import ProjectFrameworksORM
from database.frameworks import FrameworksORM

from models.admin.projects import *

from services.github import github

from typing import Dict, List, Optional


async def load_project_framework_ids():
    async with ProjectFrameworksORM() as orm: relations = await orm.find_many()

    by_project: Dict[int, List[int]] = {}

    for relation in relations:
        by_project.setdefault(relation.project_id, []).append(relation.framework_id)

    return by_project


async def framework_refs_by_id():
    async with FrameworksORM() as orm: frameworks = await orm.find_many()
    frameworks.sort(key = lambda framework: (framework.sort_order, framework.id))

    return {framework.id: FrameworkRef(**framework.dict()) for framework in frameworks}


async def validate_framework_ids(framework_ids: List[int]):
    if not framework_ids: return

    async with FrameworksORM() as orm: frameworks = await orm.find_many()
    existing_ids = {framework.id for framework in frameworks}
    invalid = set(framework_ids) - existing_ids

    if invalid: raise HTTPException(status_code = 400, detail = 'Um ou mais frameworks informados não existem.')


async def sync_relations(project_id: int, framework_ids: List[int]):
    async with ProjectFrameworksORM() as orm: await orm.delete(project_id = project_id)

    unique_ids = list(dict.fromkeys(framework_ids))
    for framework_id in unique_ids:
        async with ProjectFrameworksORM() as orm:
            await orm.create(project_id = project_id, framework_id = framework_id)


def project_framework_fields(db, framework_ids_by_project: Dict[int, List[int]], refs_by_id: Dict[int, FrameworkRef]):
    framework_ids = framework_ids_by_project.get(db.id, [])
    frameworks = [
        refs_by_id[framework_id]
        for framework_id in framework_ids
        if framework_id in refs_by_id
    ]

    return {'framework_ids': framework_ids, 'frameworks': frameworks}


async def save_translations(entity_id, translation_orm, foreign_key, by_locale):
    for locale, fields in by_locale.items():
        if locale not in ('pt', 'en') or not fields:
            continue

        filters = {foreign_key: entity_id, 'locale': locale}

        async with translation_orm() as orm:
            existing = await orm.find_one(**filters)

            if existing:
                await orm.update(id = existing.id, **fields)
            else:
                await orm.create(**filters, **fields)


def project_translations_model(project):
    grouped = {row.locale: row.dict() for row in project.translations}

    def fields(data):
        if not data:
            return None
        return ProjectTranslationFields(**{key: data.get(key) for key in ProjectTranslationFields.model_fields.keys()})

    return ProjectTranslations(pt = fields(grouped.get('pt')), en = fields(grouped.get('en')))


def translations_payload(translations: ProjectTranslations):
    return {
        'pt': translations.pt.dict() if translations.pt else None,
        'en': translations.en.dict() if translations.en else None,
    }


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


def external_project_dto(db, framework_ids_by_project: Dict[int, List[int]], refs_by_id: Dict[int, FrameworkRef]):
    translations = project_translations_model(db)
    picked = [t for t in db.translations if t.locale == 'pt']
    translation = picked[0] if picked else None
    title = translation.title or 'Projeto externo' if translation else 'Projeto externo'
    description = translation.description if translation else None

    return Project(
        git_id = db.git_id,
        name = title,
        html_url = db.repo_url or '',
        description = description,
        title = title,
        image_url = db.image_url,
        live_url = db.live_url,
        repo_url = db.repo_url,
        external = True,
        translations = translations,
        **project_framework_fields(db, framework_ids_by_project, refs_by_id),
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


def visible_project_dto(db, gh_name: str, gh_description: Optional[str], framework_ids_by_project: Dict[int, List[int]], refs_by_id: Dict[int, FrameworkRef]):
    translations = project_translations_model(db)
    picked = [t for t in db.translations if t.locale == 'pt']
    translation = picked[0] if picked else None
    title = translation.title or gh_name if translation else gh_name
    description = translation.description or gh_description if translation else gh_description

    return Project(
        git_id = db.git_id,
        name = title,
        html_url = db.repo_url or '',
        homepage = db.live_url,
        description = description,
        title = title,
        image_url = db.image_url,
        live_url = db.live_url,
        repo_url = db.repo_url,
        translations = translations,
        **project_framework_fields(db, framework_ids_by_project, refs_by_id),
    )


def github_option_dto(project):
    git_id = project['id']
    name = project['name'].replace('-', ' ').title()
    homepage = project.get('homepage') or None
    description = project.get('description') or None

    return Project(
        git_id = git_id,
        name = name,
        html_url = project.get('html_url') or '',
        homepage = homepage,
        description = description,
        **github_meta(project),
    )


def visible_project_from_github(db, project, framework_ids_by_project: Dict[int, List[int]], refs_by_id: Dict[int, FrameworkRef]):
    git_id = project['id']
    name = project['name'].replace('-', ' ').title()
    description = project.get('description') or None
    project_dto = visible_project_dto(db, name, description, framework_ids_by_project, refs_by_id)
    project_dto.private = bool(project.get('private'))
    project_dto.language = project.get('language')
    project_dto.stars = project.get('stargazers_count') or 0
    project_dto.forks = project.get('forks_count') or 0
    project_dto.updated_at = project.get('updated_at')
    project_dto.archived = bool(project.get('archived'))
    project_dto.fork = bool(project.get('fork'))
    return project_dto


async def item_data(git_id: int, is_auth: bool):
    framework_ids_by_project = await load_project_framework_ids()
    refs_by_id = await framework_refs_by_id()

    async with ProjectsORM() as orm:
        db = await orm.find_one(git_id = git_id)

    if db:
        if git_id < 0:
            return external_project_dto(db, framework_ids_by_project, refs_by_id)

        for project in github(is_auth):
            if project['id'] != git_id:
                continue
            return visible_project_from_github(db, project, framework_ids_by_project, refs_by_id)

        return external_project_dto(db, framework_ids_by_project, refs_by_id)

    if git_id > 0:
        for project in github(is_auth):
            if project['id'] != git_id:
                continue
            return github_option_dto(project)

    raise HTTPException(status_code = 404, detail = 'Projeto não encontrado.')


async def response_data(is_auth: bool):
    framework_ids_by_project = await load_project_framework_ids()
    refs_by_id = await framework_refs_by_id()

    async with ProjectsORM() as orm:
        projects_db = await orm.find_many()

    projects_mapper = {project.git_id: project for project in projects_db if project.git_id > 0}
    projects_ids = set(projects_mapper.keys())

    projects = github(is_auth)

    data = Projects()

    for project in projects:
        git_id = project['id']

        project_dto = github_option_dto(project)

        if git_id in projects_ids:
            db = projects_mapper[git_id]
            project_dto = visible_project_from_github(db, project, framework_ids_by_project, refs_by_id)
            data.visible.append(project_dto)

        else: data.options.append(project_dto)

    for db in projects_db:
        if db.git_id < 0: data.visible.append(external_project_dto(db, framework_ids_by_project, refs_by_id))

    return data


async def persist_project(git_id: int, params: ProjectPayload):
    await validate_framework_ids(params.framework_ids)

    payload = {
        'image_url': params.image_url,
        'live_url': params.live_url,
        'repo_url': params.repo_url,
    }

    async with ProjectsORM() as orm:
        project = await orm.find_one(git_id = git_id)

        if project:
            await orm.update(id = project.id, **payload)
            project = await orm.find_one(id = project.id)
        else:
            await orm.create(git_id = git_id, **payload)
            project = await orm.find_one(git_id = git_id)

        await save_translations(project.id, ProjectTranslationsORM, 'project_id', translations_payload(params.translations))
        await sync_relations(project.id, params.framework_ids)


@router.get('/projects', status_code = 200, response_model = Projects)
async def get_projects(is_auth: bool = Depends(partial_authenticated)):
    return await response_data(is_auth)


@router.get('/projects/{git_id}', status_code = 200, response_model = Project)
async def get_project(git_id: int, is_auth: bool = Depends(partial_authenticated)):
    return await item_data(git_id, is_auth)


@router.post('/projects/external', status_code = 201)
async def post_external_project(params: ProjectPayload, is_auth: bool = Depends(has_authenticated)):
    if not params.repo_url: raise HTTPException(status_code = 422, detail = 'repo_url é obrigatório para projetos externos')

    async with ProjectsORM() as orm:
        git_id = await next_external_git_id(orm)

    await persist_project(git_id, params)
    return await response_data(is_auth)


@router.post('/projects/{git_id}', status_code = 201)
async def post_projects(git_id: int, params: ProjectPayload, is_auth: bool = Depends(has_authenticated)):
    params.repo_url = params.repo_url or github_repo_url(git_id)
    await persist_project(git_id, params)
    return await response_data(is_auth)


@router.put('/projects/{git_id}', status_code = 201)
async def put_projects(git_id: int, params: ProjectPayload, is_auth: bool = Depends(has_authenticated)):
    if git_id > 0:
        params.repo_url = params.repo_url or github_repo_url(git_id)
    elif not params.repo_url:
        raise HTTPException(status_code = 422, detail = 'repo_url é obrigatório para projetos externos')

    await persist_project(git_id, params)
    return await response_data(is_auth)


@router.delete('/projects/{git_id}', status_code = 201)
async def delete_project(git_id: int, is_auth: bool = Depends(has_authenticated)):
    async with ProjectsORM() as orm: await orm.delete(git_id = git_id)
    return await response_data(is_auth)
