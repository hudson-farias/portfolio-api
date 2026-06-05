from pydantic import BaseModel


class AboutProfile(BaseModel):
    about_extended: str


class Stats(BaseModel):
    years_experience: int
    projects_count: int
    clients_count: int


class AboutResponse(BaseModel):
    profile: AboutProfile
    stats: Stats
