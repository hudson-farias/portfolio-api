from pydantic import BaseModel
from typing import List, Literal, Optional


class ExperienceTranslationFields(BaseModel):
    period: str = ''
    description: str = ''


class ExperienceTranslations(BaseModel):
    pt: Optional[ExperienceTranslationFields] = None
    en: Optional[ExperienceTranslationFields] = None


ContractType = Literal['CLT', 'PJ', 'FREELANCER']


class ExperienceBaseDTO(BaseModel):
    company: str
    role_id: Optional[int] = None
    contract_type: Optional[ContractType] = None
    live_url: Optional[str] = None
    hidden: bool = False
    translations: ExperienceTranslations


class Experience(ExperienceBaseDTO):
    id: int
    period: str
    description: str
    role_title: Optional[str] = None


class ExperienceRole(BaseModel):
    id: int
    title: str
    active: bool = True


class ExperiencesResponse(BaseModel):
    experiences: List[Experience] = []
    roles: List[ExperienceRole] = []
