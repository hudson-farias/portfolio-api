from pydantic import BaseModel
from typing import List, Literal, Optional


class Database(BaseModel):
    id: int
    name: str
    icon: str
    scope: Optional[Literal['sql', 'nosql']] = None


class DatabasesResponse(BaseModel):
    databases: List[Database] = []
