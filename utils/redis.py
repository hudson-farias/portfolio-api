from redis import Redis
from json import dumps, loads

# from env import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT

# cache = Redis(host = REDIS_HOST, port = REDIS_PORT, password = REDIS_PASSWORD, db = 0, decode_responses = True)

def set_cache(key, value, expiration_time: int = 60):
    # data = dumps(value)
    # cache.setex(key, expiration_time, data)
    return


def get_cache(key):
    # value = cache.get(key)
    # if value: return loads(value)
    return
