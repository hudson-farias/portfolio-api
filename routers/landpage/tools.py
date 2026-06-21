from fastapi import Query

from routers.landpage import router

from facades.landpage import Landpage
from models.landpage.tools import ToolsResponse
from routers.landpage import Locale


@router.get('/tools', status_code = 200, response_model = ToolsResponse)
async def get_tools(locale: Locale = Query(default = 'pt')):
    return await Landpage(locale).tools()
