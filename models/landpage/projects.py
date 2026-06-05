from pydantic import BaseModel
from typing import List, Optional


class Project(BaseModel):
    id: int
    name: str
    description: Optional[str] = ''
    image_url: Optional[str] = None
    homepage: Optional[str] = None
    html_url: Optional[str] = None


class ProjectsResponse(BaseModel):
    projects: List[Project] = []
