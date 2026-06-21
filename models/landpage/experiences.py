from pydantic import BaseModel
from typing import List, Literal, Optional

from models.landpage.__base import SocialNetwork


ContractType = Literal['CLT', 'PJ', 'FREELANCER']


class Experience(BaseModel):
    id: int
    company: str
    period: str
    role: str
    contract_type: Optional[ContractType] = None
    description: str
    live_url: Optional[str] = None


class ExperiencesResponse(BaseModel):
    experiences: List[Experience] = []
