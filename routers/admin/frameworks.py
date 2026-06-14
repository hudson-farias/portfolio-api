from fastapi import Depends, HTTPException, Query
from routers.admin import router, has_authenticated

from database.frameworks import FrameworksORM
from database.language_frameworks import LanguageFrameworksORM
from database.languages import LanguagesORM

from models.admin.frameworks import *
from models.admin.languages import Language

from services.admin_filters import filter_frameworks, filter_languages

from typing import Dict, List, Optional


async def load_relations():
    async with LanguageFrameworksORM() as orm: relations = await orm.find_many()

    framework_language_ids: Dict[int, List[int]] = {}
    for relation in relations:
        framework_language_ids.setdefault(relation.framework_id, []).append(relation.language_id)

    languages = await filter_languages()
    languages_by_id = {language.id: language for language in languages}

    return framework_language_ids, languages_by_id


async def response_data(q: Optional[str] = None):
    frameworks = await filter_frameworks(q)
    framework_language_ids, languages_by_id = await load_relations()

    data = []
    for framework in frameworks:
        linked = [
            Language(**languages_by_id[language_id].dict())
            for language_id in framework_language_ids.get(framework.id, [])
            if language_id in languages_by_id
        ]
        linked.sort(key = lambda language: (language.sort_order, language.id))
        data.append(Framework(**framework.dict(), languages = linked))

    return data


async def next_sort_order():
    async with FrameworksORM() as orm: frameworks = await orm.find_many()
    if not frameworks: return 0
    return max(framework.sort_order for framework in frameworks) + 1


async def validate_language_ids(language_ids: List[int]):
    if not language_ids: return

    async with LanguagesORM() as orm: languages = await orm.find_many()
    existing_ids = {language.id for language in languages}
    invalid = set(language_ids) - existing_ids

    if invalid: raise HTTPException(status_code = 400, detail = 'Uma ou mais linguagens informadas não existem.')


async def sync_relations(framework_id: int, language_ids: List[int]):
    async with LanguageFrameworksORM() as orm: await orm.delete(framework_id = framework_id)

    unique_ids = list(dict.fromkeys(language_ids))
    for language_id in unique_ids:
        async with LanguageFrameworksORM() as orm:
            await orm.create(framework_id = framework_id, language_id = language_id)


@router.get('/frameworks', status_code = 200, response_model = List[Framework])
async def get(q: Optional[str] = Query(None)):
    return await response_data(q)


@router.put('/frameworks/reorder', status_code = 201, response_model = List[Framework])
async def reorder(params: FrameworkReorderDTO, _: bool = Depends(has_authenticated)):
    async with FrameworksORM() as orm: frameworks = await orm.find_many()

    existing_ids = {framework.id for framework in frameworks}
    if set(params.ids) != existing_ids: raise HTTPException(status_code = 400, detail = 'Informe todos os IDs dos frameworks na nova ordem.')

    async with FrameworksORM() as orm:
        for index, framework_id in enumerate(params.ids): await orm.update(id = framework_id, sort_order = index)

    return await response_data()


@router.post('/frameworks', status_code = 201, response_model = List[Framework])
async def post(params: FrameworkWriteDTO, _: bool = Depends(has_authenticated)):
    await validate_language_ids(params.language_ids)

    payload = params.dict()
    language_ids = payload.pop('language_ids', [])
    payload['sort_order'] = await next_sort_order()

    async with FrameworksORM() as orm: await orm.create(**payload)

    async with FrameworksORM() as orm: frameworks = await orm.find_many()
    created = max(frameworks, key = lambda item: item.id) if frameworks else None
    if not created: raise HTTPException(status_code = 500, detail = 'Não foi possível criar o framework.')

    await sync_relations(created.id, language_ids)
    return await response_data()


@router.put('/frameworks/{framework_id}', status_code = 201, response_model = List[Framework])
async def put(framework_id: int, params: FrameworkWriteDTO, _: bool = Depends(has_authenticated)):
    async with FrameworksORM() as orm: current = await orm.find_one(id = framework_id)
    if not current: raise HTTPException(status_code = 404, detail = 'Framework não encontrado.')

    await validate_language_ids(params.language_ids)

    payload = params.dict()
    language_ids = payload.pop('language_ids', [])
    payload['sort_order'] = current.sort_order

    async with FrameworksORM() as orm: await orm.update(id = framework_id, **payload)
    await sync_relations(framework_id, language_ids)
    return await response_data()


@router.delete('/frameworks/{framework_id}', status_code = 201, response_model = List[Framework])
async def delete(framework_id: int, _: bool = Depends(has_authenticated)):
    async with FrameworksORM() as orm: await orm.delete(id = framework_id)
    return await response_data()
