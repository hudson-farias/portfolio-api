from fastapi import Query

from routers.landpage import router

from facades.landpage import Landpage
from models.landpage.layout import LayoutResponse
from routers.landpage import Locale


@router.get('/layout', status_code = 200, response_model = LayoutResponse)
async def get_layout(locale: Locale = Query(default = 'pt')):
    return await Landpage(locale).layout()
