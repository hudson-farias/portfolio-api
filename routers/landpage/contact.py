from routers.landpage import router

from facades.landpage import Landpage
from models.landpage.contact import ContactResponse


@router.get('/contact', status_code = 200, response_model = ContactResponse)
async def get():
    return await Landpage().contact()
