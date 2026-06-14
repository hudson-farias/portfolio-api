from pydantic import BaseModel
from typing import List, Optional


class DashboardCounts(BaseModel):
    experiences: int
    skills: int
    projects: int
    social_networks: int
    tools: int
    languages: int
    frameworks: int
    databases: int


class DashboardExperience(BaseModel):
    id: int
    company: str
    period: str
    role: str
    description: str
    hidden: bool = False


class DashboardSkill(BaseModel):
    id: int
    name: str
    icon: str


class DashboardProject(BaseModel):
    id: int
    name: str
    html_url: str
    homepage: Optional[str] = None
    description: Optional[str] = ''


class DashboardSocialNetwork(BaseModel):
    id: int
    url: str
    icon: str
    positions: List[str]


class DashboardTool(BaseModel):
    id: int
    name: str
    icon: str
    url: Optional[str] = None


class DashboardLanguage(BaseModel):
    id: int
    name: str
    icon: str


class DashboardFramework(BaseModel):
    id: int
    name: str
    icon: str
    scope: Optional[str] = None


class DashboardDatabase(BaseModel):
    id: int
    name: str
    icon: str
    scope: Optional[str] = None


class DashboardResponse(BaseModel):
    counts: DashboardCounts
    experiences: List[DashboardExperience] = []
    projects: List[DashboardProject] = []
    skills: List[DashboardSkill] = []
    social_networks: List[DashboardSocialNetwork] = []
    tools: List[DashboardTool] = []
    languages: List[DashboardLanguage] = []
    frameworks: List[DashboardFramework] = []
    databases: List[DashboardDatabase] = []
