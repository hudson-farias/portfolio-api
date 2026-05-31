from fastapi import APIRouter
from asyncio import gather

from database.social_networks import SocialNetworksORM

from models.social_networks import *


router = APIRouter()


async def get_social_networks(show_header: bool = False, show_footer: bool = False):
    params = {
        'show_header': show_header,
        'show_footer': show_footer,
    }

    async with SocialNetworksORM() as orm: social_networks = await orm.find_many(**params)
    return [SocialNetwork(**social_network.dict()) for social_network in social_networks]


@router.get('/social_networks', status_code = 200, response_model = SocialNetworks)
async def get():
    data = SocialNetworks()
    data.social_networks_header, data.social_networks_footer = await gather(get_social_networks(show_header = True), get_social_networks(show_footer = True))

    return data
