from pydantic import BaseModel
from typing import List

from models.landpage.__base import SocialNetwork


class FooterResponse(BaseModel):
    github: str
    gitlab: str
    linkedin: str
    social_networks: List[SocialNetwork] = []
