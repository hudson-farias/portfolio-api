from fastapi import Query

from routers.landpage import router

from facades.landpage import Landpage
from models.landpage.frameworks import FrameworksResponse
from routers.landpage import Locale


@router.get('/frameworks', status_code = 200, response_model = FrameworksResponse)
async def get_frameworks(locale: Locale = Query(default = 'pt')):
    return await Landpage(locale).frameworks()
