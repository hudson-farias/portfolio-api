from pydantic import BaseModel
from typing import List

from models.landpage.__base import SocialNetwork


class AboutProfile(BaseModel):
    about_extended: str


class Stats(BaseModel):
    years_experience: int
    projects_count: int
    clients_count: int


class AboutResponse(BaseModel):
    profile: AboutProfile
    stats: Stats
    social_networks: List[SocialNetwork] = []
    profile_name: str
