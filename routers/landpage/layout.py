from routers.landpage import router

from facades.landpage import Landpage
from models.landpage.layout import LayoutResponse


@router.get('/layout', status_code = 200, response_model = LayoutResponse)
async def get_layout():
    return await Landpage().layout()
