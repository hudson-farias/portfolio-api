from pydantic import BaseModel
from typing import List, Literal, Optional


class LandpageLanguageRef(BaseModel):
    id: int
    name: str
    icon: str


class Framework(BaseModel):
    id: int
    name: str
    icon: str
    scope: Optional[Literal['backend', 'frontend']] = None
    languages: List[LandpageLanguageRef] = []


class FrameworksResponse(BaseModel):
    frameworks: List[Framework] = []
