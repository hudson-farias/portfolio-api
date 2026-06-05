from routers.landpage import router

from facades.landpage import Landpage
from models.landpage.experiences import ExperiencesResponse


@router.get('/experience', status_code = 200, response_model = ExperiencesResponse)
async def get():
    return await Landpage().experiences()
