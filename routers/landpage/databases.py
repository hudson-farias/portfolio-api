from fastapi import Query

from routers.landpage import router

from facades.landpage import Landpage
from models.landpage.databases import DatabasesResponse
from routers.landpage import Locale


@router.get('/databases', status_code = 200, response_model = DatabasesResponse)
async def get_databases(locale: Locale = Query(default = 'pt')):
    return await Landpage(locale).databases()
