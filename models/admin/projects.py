from pydantic import BaseModel
from typing import Optional, List


class ProjectPayload(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    live_url: Optional[str] = None
    repo_url: Optional[str] = None


class Project(BaseModel):
    git_id: int
    name: str
    html_url: str
    homepage: Optional[str] = None
    description: Optional[str] = None
    title: Optional[str] = None
    image_url: Optional[str] = None
    live_url: Optional[str] = None
    repo_url: Optional[str] = None
    private: bool = False
    language: Optional[str] = None
    stars: int = 0
    forks: int = 0
    updated_at: Optional[str] = None
    archived: bool = False
    fork: bool = False
    external: bool = False


class Projects(BaseModel):
    visible: List[Project] = []
    options: List[Project] = []
