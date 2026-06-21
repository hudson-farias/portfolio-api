from fastapi import Depends, HTTPException, Query
from routers.admin import router, has_authenticated

from database.skills import SkillsORM

from models.admin.skills import *

from typing import Optional


async def load_skills(q: Optional[str] = None):
    async with SkillsORM() as orm:
        return await orm.find_filtered(
            q = q.strip() if q else None,
            q_columns = ['name', 'icon'],
        )


async def response_data(q: Optional[str] = None):
    skills = await load_skills(q)
    return SkillsResponse(skills = [Skill(**skill.dict()) for skill in skills])


async def item_data(skill_id: int):
    async with SkillsORM() as orm:
        skill = await orm.find_one(id = skill_id)

    if not skill:
        raise HTTPException(status_code = 404, detail = 'Skill não encontrada.')

    return Skill(**skill.dict())


@router.get('/skills', status_code = 200, response_model = SkillsResponse)
async def get(q: Optional[str] = Query(None)):
    return await response_data(q)


@router.get('/skills/{skill_id}', status_code = 200, response_model = Skill)
async def get_one(skill_id: int):
    return await item_data(skill_id)


@router.post('/skills', status_code = 201, response_model = SkillsResponse)
async def post(params: SkillDTO, _: bool = Depends(has_authenticated)):
    async with SkillsORM() as orm: await orm.create(**params.dict())
    return await response_data()


@router.put('/skills/{skill_id}', status_code = 201, response_model = SkillsResponse)
async def put(skill_id: int, params: SkillDTO, _: bool = Depends(has_authenticated)):
    async with SkillsORM() as orm: await orm.update(id = skill_id, **params.dict())
    return await response_data()


@router.delete('/skills/{skill_id}', status_code = 201, response_model = SkillsResponse)
async def delete(skill_id: int, _: bool = Depends(has_authenticated)):
    async with SkillsORM() as orm: await orm.delete(id = skill_id)
    return await response_data()
