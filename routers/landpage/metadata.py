from routers.landpage import router

from facades.landpage import Landpage
from models.landpage.metadata import MetadataResponse


@router.get('/metadata', status_code = 200, response_model = MetadataResponse)
async def get_metadata():
    return await Landpage().metadata()
