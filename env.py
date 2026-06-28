from dotenv import load_dotenv
from os import getenv
from urllib.parse import quote_plus

load_dotenv()

DOCS_PATH = getenv('DOCS_PATH')
REDOCS_PATH = getenv('REDOCS_PATH')

GITHUB_ACCESS_TOKEN = getenv('GITHUB_ACCESS_TOKEN')

AUTH_SERVICE_URL = getenv('AUTH_SERVICE_URL')

CORS_ORIGINS = getenv('CORS_ORIGINS', '')

POSTGRES_HOST = getenv('POSTGRES_HOST')
POSTGRES_USER = getenv('POSTGRES_USER')
POSTGRES_PASSWORD = getenv('POSTGRES_PASSWORD')
POSTGRES_PORT = getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = getenv('POSTGRES_DB')


def postgres_url(driver: str = 'postgresql+asyncpg') -> str:
    missing = [
        name for name, value in (
            ('POSTGRES_HOST', POSTGRES_HOST),
            ('POSTGRES_USER', POSTGRES_USER),
            ('POSTGRES_PASSWORD', POSTGRES_PASSWORD),
            ('POSTGRES_DB', POSTGRES_DB),
        )
        if not value
    ]

    if missing:
        raise RuntimeError(f'Variáveis de ambiente ausentes: {", ".join(missing)}')

    user = quote_plus(POSTGRES_USER)
    password = quote_plus(POSTGRES_PASSWORD)

    return f'{driver}://{user}:{password}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
