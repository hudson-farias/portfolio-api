from fastapi import APIRouter

from routers.auth import partial_authenticated, has_authenticated


router = APIRouter(prefix = '/admin', tags = ['admin'])
