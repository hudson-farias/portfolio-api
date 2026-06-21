from fastapi import Query

from routers.landpage import router

from facades.landpage import Landpage
from models.landpage.metadata import MetadataResponse
from routers.landpage import Locale


@router.get('/metadata', status_code = 200, response_model = MetadataResponse)
async def get_metadata(locale: Locale = Query(default = 'pt')):
    return await Landpage(locale).metadata()
