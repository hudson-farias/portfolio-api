from fastapi import Query

from routers.landpage import router

from facades.landpage import Landpage
from models.landpage.projects import ProjectsResponse
from routers.landpage import Locale


@router.get('/projects', status_code = 200, response_model = ProjectsResponse)
async def get_projects(locale: Locale = Query(default = 'pt')):
    return await Landpage(locale).projects()
