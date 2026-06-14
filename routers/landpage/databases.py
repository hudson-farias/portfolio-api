from routers.landpage import router

from facades.landpage import Landpage
from models.landpage.databases import DatabasesResponse


@router.get('/databases', status_code = 200, response_model = DatabasesResponse)
async def get_databases():
    return await Landpage().databases()
