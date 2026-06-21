from fastapi import Query

from routers.landpage import router

from routers.landpage import Locale

from facades.landpage import Landpage
from models.landpage.page import PageResponse


@router.get('/home', status_code = 200, response_model = PageResponse)
async def get_page(locale: Locale = Query(default = 'pt')):
    return await Landpage(locale).page()
