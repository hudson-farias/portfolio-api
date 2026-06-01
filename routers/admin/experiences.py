from fastapi import Depends
from routers.admin import router, partial_authenticated, has_authenticated

from database.experiences import ExperiencesORM

from models.admin.experiences import *

from typing import List


async def response_data(is_auth: bool) -> List[Experience]:
    async with ExperiencesORM() as orm:
        if is_auth: experiences = await orm.find_many()
        else: experiences = await orm.find_many(hidden = False)

    return [Experience(**experience.dict()) for experience in experiences]


@router.get('/experiences', status_code = 200, response_model = List[Experience])
async def get_experiences(is_auth: bool = Depends(partial_authenticated)):
    return await response_data(is_auth)


@router.post('/experiences', status_code = 201, response_model = List[Experience])
async def post_experience(params: ExperienceDTO, is_auth: bool = Depends(has_authenticated)):
    async with ExperiencesORM() as orm: await orm.create(**params.dict())
    return await response_data(is_auth)


@router.put('/experiences/{experience_id}', status_code = 201, response_model = List[Experience])
async def put_experience(experience_id: int, params: ExperienceDTO, is_auth: bool = Depends(has_authenticated)):
    async with ExperiencesORM() as orm: await orm.update(id = experience_id, **params.dict())
    return await response_data(is_auth)


@router.delete('/experiences/{experience_id}', status_code = 201, response_model = List[Experience])
async def delete_experience(experience_id: int, is_auth: bool = Depends(has_authenticated)):
    async with ExperiencesORM() as orm: await orm.delete(id = experience_id)
    return await response_data(is_auth)
