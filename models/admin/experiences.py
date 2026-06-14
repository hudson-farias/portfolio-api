from pydantic import BaseModel
from typing import List, Literal, Optional

ContractType = Literal['CLT', 'PJ', 'FREELANCER']


class ExperienceDTO(BaseModel):
    company: str
    period: str
    role_id: Optional[int] = None
    contract_type: Optional[ContractType] = None
    description: str
    hidden: bool = False


class Experience(ExperienceDTO):
    id: int
    role_title: Optional[str] = None


class ExperienceRole(BaseModel):
    id: int
    title: str
    locale: Optional[str] = None
    active: bool = True


class ExperiencesResponse(BaseModel):
    experiences: List[Experience] = []
    roles: List[ExperienceRole] = []
