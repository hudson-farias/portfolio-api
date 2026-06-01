from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from utils.jwt import jwt_verify


router = APIRouter(prefix = '/auth', tags = ['auth'])


def _token_from_bearer(auth: Optional[HTTPAuthorizationCredentials]) -> str | None:
    if not auth or not auth.credentials: return None
    return auth.credentials


async def partial_authenticated(auth: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error = False))):
    token = _token_from_bearer(auth)
    if not token: return False
    return jwt_verify(token)


async def has_authenticated(auth: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error = False))):
    is_auth = await partial_authenticated(auth)
    if not is_auth: raise HTTPException(status_code = 498, detail = 'Token invalid')
    return True
