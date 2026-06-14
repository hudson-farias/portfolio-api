from pydantic import BaseModel
from typing import List


class LanguageWriteDTO(BaseModel):
    name: str
    icon: str


class LanguageReorderDTO(BaseModel):
    ids: List[int]


class Language(BaseModel):
    id: int
    name: str
    icon: str
    sort_order: int
