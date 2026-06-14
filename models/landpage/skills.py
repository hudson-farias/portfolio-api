from pydantic import BaseModel
from typing import List


class Skill(BaseModel):
    id: int
    name: str
    icon: str


class SkillsResponse(BaseModel):
    skills: List[Skill] = []
