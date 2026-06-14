from routers.landpage import router

from facades.landpage import Landpage
from models.landpage.tools import ToolsResponse


@router.get('/tools', status_code = 200, response_model = ToolsResponse)
async def get_tools():
    return await Landpage().tools()
