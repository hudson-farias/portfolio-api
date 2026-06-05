from pydantic import BaseModel
from typing import List


class Experience(BaseModel):
    id: int
    company: str
    period: str
    role: str
    description: str


class ExperiencesResponse(BaseModel):
    experiences: List[Experience] = []
