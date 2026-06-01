from pydantic import BaseModel


class ExperienceDTO(BaseModel):
    company: str
    period: str
    role: str
    description: str
    hidden: bool = False


class Experience(ExperienceDTO):
    id: int
