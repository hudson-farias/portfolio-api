from fastapi import Depends
from routers.admin import router, partial_authenticated, has_authenticated

from database.roles import RolesORM

from models.admin.roles import *

from services.roles import experience_counts

from typing import List


async def response_data(is_auth: bool) -> List[Role]:
    counts = await experience_counts()

    async with RolesORM() as orm:
        if is_auth: roles = await orm.find_many()
        else: roles = await orm.find_many(active = True)

    roles.sort(key = lambda role: (role.sort_order, role.id))

    return [
        Role(
            **role.dict(),
            experience_count = counts.get(role.id, 0),
        )
        for role in roles
    ]


@router.get('/roles', status_code = 200, response_model = List[Role])
async def get(is_auth: bool = Depends(partial_authenticated)):
    return await response_data(is_auth)


@router.post('/roles', status_code = 201, response_model = List[Role])
async def post(params: RoleDTO, is_auth: bool = Depends(has_authenticated)):
    async with RolesORM() as orm:
        await orm.create(**params.dict())

    return await response_data(is_auth)


@router.put('/roles/{role_id}', status_code = 201, response_model = List[Role])
async def put(role_id: int, params: RoleDTO, is_auth: bool = Depends(has_authenticated)):
    async with RolesORM() as orm:
        await orm.update(id = role_id, **params.dict())

    return await response_data(is_auth)


@router.delete('/roles/{role_id}', status_code = 201, response_model = List[Role])
async def delete(role_id: int, is_auth: bool = Depends(has_authenticated)):
    async with RolesORM() as orm:
        await orm.delete(id = role_id)

    return await response_data(is_auth)
