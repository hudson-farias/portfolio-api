from pydantic import BaseModel
from typing import List, Optional

from models.admin.experiences import Experience
from models.admin.social_networks import SocialNetwork


class DashboardCounts(BaseModel):
    experiences: int
    skills: int
    projects: int
    social_networks: int


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


class DashboardResponse(BaseModel):
    counts: DashboardCounts
    experiences: List[Experience] = []
    projects: List[DashboardProject] = []
    skills: List[DashboardSkillCategory] = []
    social_networks_header: List[SocialNetwork] = []
    social_networks_footer: List[SocialNetwork] = []
