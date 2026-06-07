from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from jwt import encode, decode

from env import JWT_SECRET, JWT_ALGORITHM, ADMIN_AUTH, CORS_ORIGINS


OAUTH_STATE_TTL_MINUTES = 10


def _allowed_origins():
    origins = set()

    if ADMIN_AUTH:
        parsed = urlparse(ADMIN_AUTH)
        if parsed.scheme and parsed.netloc:
            origins.add(f'{parsed.scheme}://{parsed.netloc}')

    for origin in CORS_ORIGINS.split(','):
        origin = origin.strip().rstrip('/')
        if origin:
            origins.add(origin)

    return origins


def allowed_return_url(url: str | None):
    if not url:
        return None

    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return None

    origin = f'{parsed.scheme}://{parsed.netloc}'
    if origin not in _allowed_origins():
        return None

    return url


def resolve_return_url(return_url: str | None, referer: str | None = None):
    target = allowed_return_url(return_url)

    if not target and referer:
        target = allowed_return_url(referer)

    if target:
        return target

    if ADMIN_AUTH:
        return ADMIN_AUTH

    raise ValueError('ADMIN_AUTH is not configured')


def make_oauth_state(return_url: str):
    now = datetime.now(timezone.utc)
    payload = {
        'purpose': 'oauth_state',
        'return_url': return_url,
        'iat': now,
        'exp': now + timedelta(minutes = OAUTH_STATE_TTL_MINUTES),
    }

    return encode(payload, JWT_SECRET, algorithm = JWT_ALGORITHM)


def verify_oauth_state(state: str | None):
    if not state:
        return None

    try:
        payload = decode(
            state,
            JWT_SECRET,
            algorithms = [JWT_ALGORITHM],
            options = {'require': ['exp', 'return_url']},
        )
    except Exception:
        return None

    if payload.get('purpose') != 'oauth_state':
        return None

    return allowed_return_url(payload.get('return_url'))
