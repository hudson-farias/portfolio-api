from routers.landpage import router

from facades.landpage import Landpage
from models.landpage.hero import HeroResponse


@router.get('/hero', status_code = 200, response_model = HeroResponse)
async def get():
    return await Landpage().hero()
