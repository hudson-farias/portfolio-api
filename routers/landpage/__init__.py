from typing import Literal

from fastapi import APIRouter

Locale = Literal['pt', 'en']

router = APIRouter(prefix = '/landpage', tags = ['landpage'])
