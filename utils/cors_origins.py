import re
from urllib.parse import urlparse


def _wildcard_pattern(domain: str):
    escaped = domain.replace('.', r'\.')
    return re.compile(rf'^https?://([a-zA-Z0-9-]+\.)*{escaped}(:\d+)?$', re.IGNORECASE)


def parse_cors_origins(raw: str):
    exact: list[str] = []
    wildcards: list[re.Pattern[str]] = []

    for item in raw.split(','):
        entry = item.strip().rstrip('/')
        if not entry:
            continue
        if entry.startswith('*.'):
            wildcards.append(_wildcard_pattern(entry[2:]))
        else:
            exact.append(entry)

    return exact, wildcards


def is_origin_allowed(origin: str, raw: str, extra: str | None = None):
    if not origin:
        return False

    normalized = origin.rstrip('/')
    exact, wildcards = parse_cors_origins(raw)

    if normalized in exact:
        return True

    for pattern in wildcards:
        if pattern.match(normalized):
            return True

    if extra:
        parsed = urlparse(extra)
        if parsed.scheme and parsed.netloc:
            extra_origin = f'{parsed.scheme}://{parsed.netloc}'
            if normalized == extra_origin.rstrip('/'):
                return True

    return False


def cors_middleware_kwargs(raw: str):
    exact, wildcards = parse_cors_origins(raw)
    kwargs = {'allow_origins': exact}

    if wildcards:
        combined = '|'.join(pattern.pattern for pattern in wildcards)
        kwargs['allow_origin_regex'] = combined

    return kwargs
