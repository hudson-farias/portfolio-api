from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from importlib import import_module
from os.path import join
from os import walk

from env import DOCS_PATH, REDOCS_PATH, CORS_ORIGINS
from utils.rate_limit import limiter


app = FastAPI(root_path = '/api', docs_url = DOCS_PATH, redoc_url = REDOCS_PATH)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_cors_origins = [origin.strip() for origin in CORS_ORIGINS.split(',') if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins = _cors_origins or [],
    allow_credentials = True,
    allow_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
    allow_headers = ['Authorization', 'Content-Type'],
)

def load(subapp: FastAPI, directory: str = 'routers'):
    import_cache = {}

    for root, _, files in walk(directory):
        for file in files:
            if not file.startswith('__') and file.endswith('.py'):
                path = join(root, file).replace('.py', '').replace('/', '.').replace('\\', '.')

                if path not in import_cache:
                    import_cache[path] = import_module(path)

    included_routers = set()

    for module in import_cache.values():
        router_id = id(module.router)

        if router_id in included_routers:
            continue

        included_routers.add(router_id)
        subapp.include_router(module.router)

    del import_cache

load(app)
