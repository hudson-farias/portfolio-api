from pydantic import BaseModel

from models.landpage.about import AboutResponse
from models.landpage.contact import ContactResponse
from models.landpage.experiences import ExperiencesResponse
from models.landpage.hero import HeroResponse
from models.landpage.projects import ProjectsResponse
from models.landpage.skills import SkillsResponse


class LandpageResponse(BaseModel):
    about: AboutResponse
    contact: ContactResponse
    experiences: ExperiencesResponse
    hero: HeroResponse
    projects: ProjectsResponse
    skills: SkillsResponse
