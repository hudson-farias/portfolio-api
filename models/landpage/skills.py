from pydantic import BaseModel
from typing import List


class Skill(BaseModel):
    id: int
    name: str
    icon: str


class SkillCategory(BaseModel):
    title: str
    skills: List[Skill] = []


class SkillsResponse(BaseModel):
    skills: List[SkillCategory] = []
