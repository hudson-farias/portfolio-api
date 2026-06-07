from pydantic import BaseModel
from typing import Literal, Optional

Seniority = Literal['Junior', 'Pleno', 'Senior', 'Lead']
Locale = Literal['pt', 'en', 'todos']


class RoleDTO(BaseModel):
    title: str
    summary: Optional[str] = None
    category: Optional[str] = None
    seniority: Optional[Seniority] = None
    show: bool = False
    featured: bool = False
    locale: Locale = 'pt'
    active: bool = True
    sort_order: int = 0
    color: Optional[str] = None
    icon: Optional[str] = None


class Role(RoleDTO):
    id: int
    experience_count: int = 0
