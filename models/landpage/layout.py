from pydantic import BaseModel

from models.landpage.contact import ContactResponse
from models.landpage.footer import FooterResponse
from models.landpage.hero import HeroResponse


class LayoutResponse(BaseModel):
    hero: HeroResponse
    footer: FooterResponse
    contact: ContactResponse
