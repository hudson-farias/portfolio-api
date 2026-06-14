from fastapi import Depends
from routers.admin import router, has_authenticated

from database.profile import ProfileORM

from models.admin.profile import *


async def response_data() -> Profile:
    async with ProfileORM() as orm: profile = await orm.find_one()
    return Profile(**profile.dict())


@router.get('/profile', status_code = 200, response_model = Profile)
async def get():
    return await response_data()


@router.put('/profile', status_code = 201, response_model = Profile)
async def put(params: Profile, _: bool = Depends(has_authenticated)):
    async with ProfileORM() as orm:
        profile = await orm.find_one()
        await orm.update(id = profile.id, **params.dict())

    return await response_data()
