from fastapi import Depends, Query
from routers.admin import router, has_authenticated

from database.social_networks import SocialNetworksORM

from models.admin.social_networks import *

from typing import List, Optional


async def load_social_networks(q: Optional[str] = None, position: Optional[str] = None):
    array_contains = {'positions': position} if position else None

    async with SocialNetworksORM() as orm:
        return await orm.find_filtered(
            q = q.strip() if q else None,
            q_columns = ['url', 'icon'],
            array_contains = array_contains,
        )


async def response_data(q: Optional[str] = None, position: Optional[str] = None):
    social_networks = await load_social_networks(q, position)
    return [SocialNetwork(**social_network.dict()) for social_network in social_networks]


@router.get('/social_networks', status_code = 200, response_model = List[SocialNetwork])
async def get(q: Optional[str] = Query(None), position: Optional[str] = Query(None)):
    return await response_data(q, position)


@router.post('/social_networks', status_code = 201, response_model = List[SocialNetwork])
async def post(params: SocialNetworkDTO, _: bool = Depends(has_authenticated)):
    async with SocialNetworksORM() as orm: await orm.create(**params.dict())
    return await response_data()


@router.put('/social_networks/{social_network_id}', status_code = 201, response_model = List[SocialNetwork])
async def put(social_network_id: int, params: SocialNetworkDTO, _: bool = Depends(has_authenticated)):
    async with SocialNetworksORM() as orm: await orm.update(id = social_network_id, **params.dict())
    return await response_data()


@router.delete('/social_networks/{social_network_id}', status_code = 201, response_model = List[SocialNetwork])
async def delete(social_network_id: int, _: bool = Depends(has_authenticated)):
    async with SocialNetworksORM() as orm: await orm.delete(id = social_network_id)
    return await response_data()
