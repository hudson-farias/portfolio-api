from pydantic import BaseModel
from typing import List


class SocialNetwork(BaseModel):
    id: int
    url: str
    icon: str


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
