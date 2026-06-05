from routers.landpage import router

from facades.landpage import Landpage
from models.landpage.skills import SkillsResponse


@router.get('/skills', status_code = 200, response_model = SkillsResponse)
async def get():
    return await Landpage().skills()
