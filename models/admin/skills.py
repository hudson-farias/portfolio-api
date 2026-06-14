from pydantic import BaseModel
from typing import List


class SkillDTO(BaseModel):
    name: str
    icon: str


class Skill(SkillDTO):
    id: int


class SkillsResponse(BaseModel):
    skills: List[Skill] = []
