from pydantic import BaseModel


class SocialNetwork(BaseModel):
    icon: str
    url: str
