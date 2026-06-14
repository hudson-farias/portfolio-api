from fastapi import Depends, Query
from routers.admin import router, partial_authenticated, has_authenticated

from database.roles import RolesORM

from models.admin.roles import *

from services.roles import experience_counts
from services.admin_filters import filter_roles

from typing import List, Optional


async def response_data(is_auth: bool, q: Optional[str] = None, locale: Optional[str] = None, seniority: Optional[Seniority] = None, show: Optional[bool] = None, active: Optional[bool] = None, featured: Optional[bool] = None):
    counts = await experience_counts()
    roles = await filter_roles(is_auth, q, locale, seniority, show, active, featured)

    return [
        Role(
            **role.dict(),
            experience_count = counts.get(role.id, 0),
        )
        for role in roles
    ]


@router.get('/roles', status_code = 200, response_model = List[Role])
async def get(is_auth: bool = Depends(partial_authenticated), q: Optional[str] = Query(None), locale: Optional[str] = Query(None), seniority: Optional[Seniority] = Query(None), show: Optional[bool] = Query(None), active: Optional[bool] = Query(None), featured: Optional[bool] = Query(None)):
    return await response_data(is_auth, q, locale, seniority, show, active, featured)


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
