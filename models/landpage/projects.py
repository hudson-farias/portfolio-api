from pydantic import BaseModel
from typing import List, Optional

from models.landpage.frameworks import LandpageFrameworkRef


class Project(BaseModel):
    id: int
    name: str
    description: Optional[str] = ''
    image_url: Optional[str] = None
    homepage: Optional[str] = None
    html_url: Optional[str] = None
    frameworks: List[LandpageFrameworkRef] = []


class ProjectsResponse(BaseModel):
    projects: List[Project] = []
