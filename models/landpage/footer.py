from pydantic import BaseModel
from typing import List

from models.landpage.__base import SocialNetwork


class FooterResponse(BaseModel):
    social_networks: List[SocialNetwork] = []
