from routers.landpage import router

from facades.landpage import Landpage
from models.landpage.projects import ProjectsResponse


@router.get('/projects', status_code = 200, response_model = ProjectsResponse)
async def get_projects():
    return await Landpage().projects()
