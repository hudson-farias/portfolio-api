from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials
from typing import Optional

from env import COOKIE_DOMAIN, COOKIE_SECURE, JWT_EXPIRES_DAYS


AUTH_COOKIE = 'ACCESS_TOKEN_ADMIN'
AUTH_COOKIE_MAX_AGE = JWT_EXPIRES_DAYS * 86400


def _cookie_kwargs():
    kwargs = {
        'key': AUTH_COOKIE,
        'path': '/',
        'httponly': True,
        'secure': COOKIE_SECURE,
        'samesite': 'lax',
        'max_age': AUTH_COOKIE_MAX_AGE,
    }

    if COOKIE_DOMAIN:
        kwargs['domain'] = COOKIE_DOMAIN

    return kwargs


def set_auth_cookie(response: Response, token: str):
    response.set_cookie(value = token, **_cookie_kwargs())


def clear_auth_cookie(response: Response):
    kwargs = _cookie_kwargs()
    kwargs.pop('max_age', None)
    response.delete_cookie(**kwargs)


def redirect_with_auth_cookie(token: str, url: str):
    response = RedirectResponse(url = url, status_code = 302)
    set_auth_cookie(response, token)
    return response


def token_from_bearer(auth: Optional[HTTPAuthorizationCredentials]):
    if not auth or not auth.credentials:
        return None

    return auth.credentials


def token_from_request(request: Request, auth: Optional[HTTPAuthorizationCredentials] = None):
    return token_from_bearer(auth) or request.cookies.get(AUTH_COOKIE)
