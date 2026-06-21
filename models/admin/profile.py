from pydantic import BaseModel
from typing import Optional


class ProfileTranslationFields(BaseModel):
    summary: str = ''
    about_me: str = ''
    location: str = ''


class ProfileTranslations(BaseModel):
    pt: Optional[ProfileTranslationFields] = None
    en: Optional[ProfileTranslationFields] = None


class Profile(BaseModel):
    name: str
    last_name: str = ''
    available: bool = True
    email: str
    whatsapp: str
    linkedin: str
    github: str
    gitlab: str
    translations: ProfileTranslations


class ProfileWrite(BaseModel):
    name: str
    last_name: str = ''
    available: bool = True
    email: str
    whatsapp: str
    linkedin: str
    github: str
    gitlab: str
    translations: ProfileTranslations
