from pydantic import BaseModel
from typing import Literal, Optional

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
