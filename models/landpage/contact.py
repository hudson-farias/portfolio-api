from pydantic import BaseModel
from typing import List, Optional

from models.landpage.__base import SocialNetwork


class ContactResponse(BaseModel):
    email: Optional[str] = 'hudson.farias.dev@gmail.com'
    others: List[SocialNetwork] = []
