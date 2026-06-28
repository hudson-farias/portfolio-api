from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

import httpx

from env import AUTH_SERVICE_URL

router = APIRouter(prefix = '/admin', tags = ['admin'])

AUTH_COOKIE = 'ACCESS_TOKEN_ADMIN'
_bearer = HTTPBearer(auto_error = False)


def _verify_headers(request: Request, auth: Optional[HTTPAuthorizationCredentials]):
    headers = {}
    token = request.cookies.get(AUTH_COOKIE)

    if token: headers['Cookie'] = f'{AUTH_COOKIE}={token}'
    elif auth and auth.credentials: headers['Authorization'] = f'Bearer {auth.credentials}'

    return headers


async def _auth_service_valid(request: Request, auth: Optional[HTTPAuthorizationCredentials]):
    base = (AUTH_SERVICE_URL or '').rstrip('/')
    if not base:
        return False

    headers = _verify_headers(request, auth)
    if not headers:
        return False

    try:
        async with httpx.AsyncClient(timeout = 5.0) as client:
            response = await client.get(f'{base}/auth/verify', headers = headers)
    except httpx.HTTPError:
        return False

    return response.status_code == 204


async def partial_authenticated(request: Request, auth: Optional[HTTPAuthorizationCredentials] = Depends(_bearer)):
    return await _auth_service_valid(request, auth)


async def has_authenticated(request: Request, auth: Optional[HTTPAuthorizationCredentials] = Depends(_bearer)):
    is_auth = await partial_authenticated(request, auth)
    if not is_auth: raise HTTPException(status_code = 498, detail = 'Token invalid')
    return True
