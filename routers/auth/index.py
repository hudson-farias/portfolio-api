from fastapi import Response, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials
from typing import Optional
from urllib.parse import urlencode, urlparse, parse_qsl, urlunparse

from httpx import get, post

from routers.auth import router, _bearer
from utils.jwt import jwt_maker, jwt_verify
from utils.auth_cookie import token_from_request, redirect_with_auth_cookie, clear_auth_cookie
from utils.oauth_state import make_oauth_state, verify_oauth_state, resolve_return_url
from utils.rate_limit import limiter

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
@limiter.limit('10/minute')
async def discord_auth(request: Request, code: str | None = None, state: str | None = None, error: str | None = None,):
    if error: return _redirect_callback(auth = 'discord_denied')

    if not code: return _redirect_callback(auth = 'missing')

    return_url = verify_oauth_state(state) or ADMIN_AUTH

    discord_access = _discord_token(code)
    if not discord_access: return _redirect_callback(auth = 'discord_token')

    email = _discord_user_email(discord_access)
    if not email or email not in OWNER_EMAIL_SET: return _redirect_callback(auth = 'denied')

    app_token = jwt_maker(email)
    return redirect_with_auth_cookie(app_token, return_url)


@router.get('/discord/redirect')
@limiter.limit('20/minute')
async def discord_redirect(request: Request, return_url: str | None = None):
    try: target = resolve_return_url(return_url, request.headers.get('Referer'))
    except ValueError: raise HTTPException(status_code = 400, detail = 'ADMIN_AUTH is not configured')

    state = make_oauth_state(target)

    authorize = (
        f'https://discord.com/oauth2/authorize'
        f'?client_id={DISCORD_CLIENT_ID}'
        f'&response_type=code'
        f'&scope=email+identify'
        f'&redirect_uri={DISCORD_REDIRECT_URI}'
        f'&state={state}'
    )
    return RedirectResponse(url = authorize)


@router.get('/verify')
@limiter.limit('60/minute')
async def verify_token(request: Request, response: Response, auth: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),):
    jwt_token = token_from_request(request, auth)
    if not jwt_token:
        raise HTTPException(status_code = 401, detail = 'Token not found')

    if not jwt_verify(jwt_token):
        response.status_code = 498
        return response

    response.status_code = 204
    return response


@router.get('/logout')
@limiter.limit('20/minute')
async def logout(request: Request, redirect: str | None = None):
    try: target = resolve_return_url(redirect)
    except ValueError: raise HTTPException(status_code = 400, detail = 'ADMIN_AUTH is not configured')

    response = RedirectResponse(url = target, status_code = 302)
    clear_auth_cookie(response)
    return response
