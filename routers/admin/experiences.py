from fastapi import Depends, Query
from routers.admin import router, partial_authenticated, has_authenticated

from database.experiences import ExperiencesORM
from database.roles import RolesORM

from models.admin.experiences import *

from services.admin_filters import filter_experiences
from utils.sanitize import sanitize_html

from typing import Optional

async def response_data(is_auth: bool, q: Optional[str] = None, role_id: Optional[int] = None, contract_type: Optional[ContractType] = None, hidden: Optional[bool] = None):
    experiences = await filter_experiences(is_auth, q, role_id, contract_type, hidden)
    async with RolesORM() as orm: roles = await orm.find_many()

    return ExperiencesResponse(
        experiences = [Experience(**experience.dict(), role_title = experience.role_title) for experience in experiences],
        roles = [ExperienceRole(id = role.id, title = role.title, locale = role.locale, active = role.active) for role in roles],
    )


@router.get('/experiences', status_code = 200, response_model = ExperiencesResponse)
async def get_experiences(is_auth: bool = Depends(partial_authenticated), q: Optional[str] = Query(None), role_id: Optional[int] = Query(None), contract_type: Optional[ContractType] = Query(None), hidden: Optional[bool] = Query(None)):
    return await response_data(is_auth, q, role_id, contract_type, hidden)


@router.post('/experiences', status_code = 201, response_model = ExperiencesResponse)
async def post_experience(params: ExperienceDTO, is_auth: bool = Depends(has_authenticated)):
    data = params.dict()
    data['description'] = sanitize_html(data['description'])

    async with ExperiencesORM() as orm: await orm.create(**data)

    return await response_data(is_auth)


@router.put('/experiences/{experience_id}', status_code = 201, response_model = ExperiencesResponse)
async def put_experience(experience_id: int, params: ExperienceDTO, is_auth: bool = Depends(has_authenticated)):
    data = params.dict()
    data['description'] = sanitize_html(data['description'])

    async with ExperiencesORM() as orm: await orm.update(id = experience_id, **data)

    return await response_data(is_auth)


@router.delete('/experiences/{experience_id}', status_code = 201, response_model = ExperiencesResponse)
async def delete_experience(experience_id: int, is_auth: bool = Depends(has_authenticated)):
    async with ExperiencesORM() as orm: await orm.delete(id = experience_id)

    return await response_data(is_auth)
