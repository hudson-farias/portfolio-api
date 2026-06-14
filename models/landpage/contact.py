from pydantic import BaseModel
from typing import List

from models.landpage.__base import SocialNetwork


class ContactResponse(BaseModel):
    email: str
    whatsapp_url: str
    linkedin: str
    github: str
    gitlab: str
    others: List[SocialNetwork] = []
    profile_name: str
