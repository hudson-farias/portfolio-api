from pydantic import BaseModel


class Profile(BaseModel):
    name: str
    last_name: str = ''
    summary: str
    about_me: str
    location: str = ''
    available: bool = True
    email: str
    whatsapp: str
    linkedin: str
    github: str
    gitlab: str
