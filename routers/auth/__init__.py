from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from utils.jwt import jwt_verify
from utils.auth_cookie import token_from_request


router = APIRouter(prefix = '/auth', tags = ['auth'])
_bearer = HTTPBearer(auto_error = False)


async def partial_authenticated(request: Request, auth: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),):
    token = token_from_request(request, auth)
    if not token: return False
    return jwt_verify(token)


async def has_authenticated(request: Request, auth: Optional[HTTPAuthorizationCredentials] = Depends(_bearer)):
    is_auth = await partial_authenticated(request, auth)
    if not is_auth: raise HTTPException(status_code = 498, detail = 'Token invalid')
    return True
