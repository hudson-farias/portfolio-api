from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jwt import encode, decode

from env import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRES_DAYS


def jwt_maker(email: str):
    now = datetime.now(timezone.utc)
    payload = {
        'sub': email,
        'iat': now,
        'exp': now + timedelta(days = JWT_EXPIRES_DAYS),
        'jti': str(uuid4()),
    }

    return encode(payload, JWT_SECRET, algorithm = JWT_ALGORITHM)


def jwt_verify(token: str):
    try:
        decode(
            token,
            JWT_SECRET,
            algorithms = [JWT_ALGORITHM],
            options = {'require': ['exp', 'sub', 'jti']},
        )
    except Exception:
        return False

    return True
