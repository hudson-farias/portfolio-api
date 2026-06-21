from fastapi import Depends, HTTPException, Query
from routers.admin import router, has_authenticated

from database.languages import LanguagesORM

from models.admin.languages import *

from typing import List, Optional


async def load_languages(q: Optional[str] = None):
    async with LanguagesORM() as orm:
        languages = await orm.find_filtered(
            q = q.strip() if q else None,
            q_columns = ['name', 'icon'],
        )

    languages.sort(key = lambda language: (language.sort_order, language.id))
    return languages


async def response_data(q: Optional[str] = None):
    languages = await load_languages(q)
    return [Language(**language.dict()) for language in languages]


async def next_sort_order():
    async with LanguagesORM() as orm: languages = await orm.find_many()
    if not languages: return 0
    return max(language.sort_order for language in languages) + 1


async def item_data(language_id: int):
    async with LanguagesORM() as orm:
        language = await orm.find_one(id = language_id)

    if not language:
        raise HTTPException(status_code = 404, detail = 'Linguagem não encontrada.')

    return Language(**language.dict())


@router.get('/languages', status_code = 200, response_model = List[Language])
async def get(q: Optional[str] = Query(None)):
    return await response_data(q)


@router.get('/languages/{language_id}', status_code = 200, response_model = Language)
async def get_one(language_id: int):
    return await item_data(language_id)


@router.put('/languages/reorder', status_code = 201, response_model = List[Language])
async def reorder(params: LanguageReorderDTO, _: bool = Depends(has_authenticated)):
    async with LanguagesORM() as orm: languages = await orm.find_many()

    existing_ids = {language.id for language in languages}
    if set(params.ids) != existing_ids: raise HTTPException(status_code = 400, detail = 'Informe todos os IDs das linguagens na nova ordem.')

    async with LanguagesORM() as orm:
        for index, language_id in enumerate(params.ids): await orm.update(id = language_id, sort_order = index)

    return await response_data()


@router.post('/languages', status_code = 201, response_model = List[Language])
async def post(params: LanguageWriteDTO, _: bool = Depends(has_authenticated)):
    payload = params.dict()
    payload['sort_order'] = await next_sort_order()

    async with LanguagesORM() as orm: await orm.create(**payload)
    return await response_data()


@router.put('/languages/{language_id}', status_code = 201, response_model = List[Language])
async def put(language_id: int, params: LanguageWriteDTO, _: bool = Depends(has_authenticated)):
    async with LanguagesORM() as orm: current = await orm.find_one(id = language_id)
    if not current: raise HTTPException(status_code = 404, detail = 'Linguagem não encontrada.')

    payload = params.dict()
    payload['sort_order'] = current.sort_order

    async with LanguagesORM() as orm: await orm.update(id = language_id, **payload)
    return await response_data()


@router.delete('/languages/{language_id}', status_code = 201, response_model = List[Language])
async def delete(language_id: int, _: bool = Depends(has_authenticated)):
    async with LanguagesORM() as orm: await orm.delete(id = language_id)
    return await response_data()
