from fastapi import Depends, HTTPException, Query
from routers.admin import router, has_authenticated

from database.databases import DatabasesORM

from models.admin.databases import *

from typing import List, Optional


async def load_databases(q: Optional[str] = None):
    async with DatabasesORM() as orm:
        databases = await orm.find_filtered(
            q = q.strip() if q else None,
            q_columns = ['name', 'icon', 'scope'],
        )

    databases.sort(key = lambda database: (database.sort_order, database.id))
    return databases


async def response_data(q: Optional[str] = None):
    databases = await load_databases(q)
    return [Database(**database.dict()) for database in databases]


async def next_sort_order():
    async with DatabasesORM() as orm: databases = await orm.find_many()
    if not databases: return 0
    return max(database.sort_order for database in databases) + 1


async def item_data(database_id: int):
    async with DatabasesORM() as orm:
        database = await orm.find_one(id = database_id)

    if not database:
        raise HTTPException(status_code = 404, detail = 'Banco de dados não encontrado.')

    return Database(**database.dict())


@router.get('/databases', status_code = 200, response_model = List[Database])
async def get(q: Optional[str] = Query(None)):
    return await response_data(q)


@router.get('/databases/{database_id}', status_code = 200, response_model = Database)
async def get_one(database_id: int):
    return await item_data(database_id)


@router.put('/databases/reorder', status_code = 201, response_model = List[Database])
async def reorder(params: DatabaseReorderDTO, _: bool = Depends(has_authenticated)):
    async with DatabasesORM() as orm: databases = await orm.find_many()

    existing_ids = {database.id for database in databases}
    if set(params.ids) != existing_ids: raise HTTPException(status_code = 400, detail = 'Informe todos os IDs dos bancos na nova ordem.')

    async with DatabasesORM() as orm:
        for index, database_id in enumerate(params.ids): await orm.update(id = database_id, sort_order = index)

    return await response_data()


@router.post('/databases', status_code = 201, response_model = List[Database])
async def post(params: DatabaseWriteDTO, _: bool = Depends(has_authenticated)):
    payload = params.dict()
    payload['sort_order'] = await next_sort_order()

    async with DatabasesORM() as orm: await orm.create(**payload)
    return await response_data()


@router.put('/databases/{database_id}', status_code = 201, response_model = List[Database])
async def put(database_id: int, params: DatabaseWriteDTO, _: bool = Depends(has_authenticated)):
    async with DatabasesORM() as orm: current = await orm.find_one(id = database_id)
    if not current: raise HTTPException(status_code = 404, detail = 'Banco de dados não encontrado.')

    payload = params.dict()
    payload['sort_order'] = current.sort_order

    async with DatabasesORM() as orm: await orm.update(id = database_id, **payload)
    return await response_data()


@router.delete('/databases/{database_id}', status_code = 201, response_model = List[Database])
async def delete(database_id: int, _: bool = Depends(has_authenticated)):
    async with DatabasesORM() as orm: await orm.delete(id = database_id)
    return await response_data()
