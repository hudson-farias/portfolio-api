from pydantic import BaseModel
from typing import List


class SocialNetworkDTO(BaseModel):
    url: str
    icon: str
    positions: List[str]


class SocialNetwork(SocialNetworkDTO):
    id: int
