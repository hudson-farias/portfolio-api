from routers.landpage import router

from facades.landpage import Landpage
from models.landpage.page import PageResponse


@router.get('/home', status_code = 200, response_model = PageResponse)
async def get_page():
    return await Landpage().page()
