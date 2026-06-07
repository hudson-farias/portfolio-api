from pydantic import BaseModel
from typing import List, Literal, Optional

ContractType = Literal['CLT', 'PJ', 'FREELANCER']


class Experience(BaseModel):
    id: int
    company: str
    period: str
    role: str
    contract_type: Optional[ContractType] = None
    description: str


class ExperiencesResponse(BaseModel):
    experiences: List[Experience] = []
