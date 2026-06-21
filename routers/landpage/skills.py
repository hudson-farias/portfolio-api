from fastapi import Query

from routers.landpage import router

from facades.landpage import Landpage
from models.landpage.skills import SkillsResponse
from routers.landpage import Locale


@router.get('/skills', status_code = 200, response_model = SkillsResponse)
async def get_skills(locale: Locale = Query(default = 'pt')):
    return await Landpage(locale).skills()
