from routers.landpage import router

from facades.landpage import Landpage
from models.landpage.frameworks import FrameworksResponse


@router.get('/frameworks', status_code = 200, response_model = FrameworksResponse)
async def get_frameworks():
    return await Landpage().frameworks()
