from pydantic import BaseModel
from typing import List


class MetadataResponse(BaseModel):
    name: str
    roles: List[str]
    about: str
