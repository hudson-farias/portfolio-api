from pydantic import BaseModel
from typing import List, Literal, Optional


DatabaseScope = Literal['sql', 'nosql']


class DatabaseWriteDTO(BaseModel):
    name: str
    icon: str
    scope: Optional[DatabaseScope] = None


class DatabaseReorderDTO(BaseModel):
    ids: List[int]


class Database(BaseModel):
    id: int
    name: str
    icon: str
    scope: Optional[DatabaseScope] = None
    sort_order: int
