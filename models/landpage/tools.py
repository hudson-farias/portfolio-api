from pydantic import BaseModel
from typing import List, Optional


class Tool(BaseModel):
    id: int
    name: str
    icon: str
    url: Optional[str] = None


class ToolsResponse(BaseModel):
    tools: List[Tool] = []
