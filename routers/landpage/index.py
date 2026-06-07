from routers.landpage import router

from facades.landpage import Landpage
from models.landpage.landpage import LandpageResponse


@router.get('/landpage', status_code = 200, response_model = LandpageResponse)
async def get():
    return await Landpage().all()
