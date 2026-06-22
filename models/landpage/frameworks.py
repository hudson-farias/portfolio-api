from pydantic import BaseModel
from typing import List, Literal, Optional


class LandpageLanguageRef(BaseModel):
    id: int
    name: str
    icon: str


class LandpageFrameworkRef(BaseModel):
    id: int
    name: str
    icon: str
    languages: List[LandpageLanguageRef] = []


class Framework(BaseModel):
    id: int
    name: str
    icon: str
    scope: Optional[Literal['backend', 'frontend', 'fullstack', 'mobile', 'automation', 'other']] = None
    languages: List[LandpageLanguageRef] = []


class FrameworksResponse(BaseModel):
    frameworks: List[Framework] = []
