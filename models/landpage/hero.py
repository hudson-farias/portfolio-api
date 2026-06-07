from pydantic import BaseModel
from typing import List, Optional

from models.landpage.__base import SocialNetwork


class HeroProfile(BaseModel):
    name: str
    roles: List[str]
    location: str
    email: Optional[str] = 'hudson.farias.dev@gmail.com'
    about: str
    available: bool


class HeroResponse(BaseModel):
    profile: HeroProfile
    social_networks: List[SocialNetwork] = []
