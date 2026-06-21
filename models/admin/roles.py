from pydantic import BaseModel
from typing import Literal, List, Optional


class RoleTranslationFields(BaseModel):
    title: str = ''
    summary: Optional[str] = None


class RoleTranslations(BaseModel):
    pt: Optional[RoleTranslationFields] = None
    en: Optional[RoleTranslationFields] = None


Seniority = Literal['Junior', 'Pleno', 'Senior', 'Lead']


class RoleDTO(BaseModel):
    category: Optional[str] = None
    seniority: Optional[Seniority] = None
    show: bool = False
    featured: bool = False
    active: bool = True
    sort_order: int = 0
    color: Optional[str] = None
    icon: Optional[str] = None
    translations: RoleTranslations


class Role(RoleDTO):
    id: int
    title: str
    experience_count: int = 0
