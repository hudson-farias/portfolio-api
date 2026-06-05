from pydantic import BaseModel
from typing import List, Optional


class DashboardCounts(BaseModel):
    experiences: int
    skills: int
    projects: int
    social_networks: int


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


class DashboardSkillCategory(BaseModel):
    title: str
    skills: List[DashboardSkill] = []


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
    show_header: bool
    show_footer: bool


class DashboardResponse(BaseModel):
    counts: DashboardCounts
    experiences: List[DashboardExperience] = []
    projects: List[DashboardProject] = []
    skills: List[DashboardSkillCategory] = []
    social_networks_header: List[DashboardSocialNetwork] = []
    social_networks_footer: List[DashboardSocialNetwork] = []
