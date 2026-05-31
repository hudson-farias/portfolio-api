from fastapi import Response, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from urllib.parse import urlencode, urlparse, parse_qsl, urlunparse

from httpx import get, post

from routers.auth import router, _token_from_bearer
from utils.jwt import jwt_maker, jwt_verify
from utils.redis import set_cache

from env import DISCORD_REDIRECT_URI, DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, OWNER_EMAILS, ADMIN_AUTH

API_ENDPOINT = 'https://discord.com/api'
OWNER_EMAIL_SET = { email.strip().lower() for email in OWNER_EMAILS if email.strip() }


def _append_query(url: str, params: dict[str, str]):
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query))
    query.update(params)
    return urlunparse(parsed._replace(query = urlencode(query)))



def _redirect_callback(**query: str):
    return RedirectResponse(url = _append_query(ADMIN_AUTH, query))


def _discord_token(code: str):
    payload = {
        'grant_type': 'authorization_code',
        'redirect_uri': DISCORD_REDIRECT_URI,
        'code': code,
    }
    headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
    response = post(
        f'{API_ENDPOINT}/oauth2/token',
        data = payload,
        headers = headers,
        auth = (DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET),
    )
    if response.status_code != 200:
        return None
    return response.json().get('access_token')


def _discord_user_email(access_token: str):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Bearer {access_token}',
    }
    response = get(f'{API_ENDPOINT}/users/@me', headers = headers)
    if response.status_code != 200:
        return None
    email = response.json().get('email')
    return email.strip().lower() if isinstance(email, str) else None


@router.get('/discord')
async def discord_auth(code: str | None = None, error: str | None = None):
    if error: return _redirect_callback(auth = 'discord_denied')

    if not code: return _redirect_callback(auth = 'missing')

    discord_access = _discord_token(code)
    if not discord_access: return _redirect_callback(auth = 'discord_token')

    email = _discord_user_email(discord_access)
    if not email or email not in OWNER_EMAIL_SET: return _redirect_callback(auth = 'denied')

    app_token = jwt_maker()
    return _redirect_callback(token = app_token)


@router.get('/discord/redirect')
async def discord_redirect(request: Request, return_url: str | None = None):
    target = return_url or request.headers.get('Referer') or ADMIN_AUTH
    if not target: raise HTTPException(status_code = 400, detail = 'return_url is required')

    set_cache('JWT-LAST-URL', target)

    authorize = (
        f'https://discord.com/oauth2/authorize'
        f'?client_id={DISCORD_CLIENT_ID}'
        f'&response_type=code'
        f'&scope=email+identify'
        f'&redirect_uri={DISCORD_REDIRECT_URI}'
    )
    return RedirectResponse(url = authorize)


@router.get('/verify')
async def verify_token(response: Response, token: str | None = None, auth: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error = False))):
    jwt_token = _token_from_bearer(auth) or token
    if not jwt_token:
        raise HTTPException(status_code = 401, detail = 'Token not found')

    if not jwt_verify(jwt_token):
        response.status_code = 498
        return response

    response.status_code = 204
    return response
