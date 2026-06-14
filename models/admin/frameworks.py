from pydantic import BaseModel
from typing import List, Literal, Optional

from models.admin.languages import Language


FrameworkScope = Literal['backend', 'frontend']


class FrameworkWriteDTO(BaseModel):
    name: str
    icon: str
    scope: Optional[FrameworkScope] = None
    language_ids: List[int] = []


class FrameworkReorderDTO(BaseModel):
    ids: List[int]


class Framework(BaseModel):
    id: int
    name: str
    icon: str
    scope: Optional[FrameworkScope] = None
    sort_order: int
    languages: List[Language] = []
