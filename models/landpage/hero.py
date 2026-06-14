from pydantic import BaseModel
from typing import List

from models.landpage.__base import SocialNetwork


class HeroProfile(BaseModel):
    name: str
    roles: List[str]
    location: str
    email: str
    about: str
    available: bool


class HeroResponse(BaseModel):
    profile: HeroProfile
    social_networks: List[SocialNetwork] = []
