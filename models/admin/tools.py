from pydantic import BaseModel
from typing import List, Optional


class ToolWriteDTO(BaseModel):
    name: str
    icon: str
    url: Optional[str] = None


class ToolReorderDTO(BaseModel):
    ids: List[int]


class Tool(ToolWriteDTO):
    id: int
    sort_order: int
