from routers.landpage import router

from facades.landpage import Landpage
from models.landpage.about import AboutResponse


@router.get('/about', status_code = 200, response_model = AboutResponse)
async def get():
    return await Landpage().about()
