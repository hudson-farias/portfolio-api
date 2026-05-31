from jwt import encode, decode
from env import JWT_SECRET, JWT_ALGORITHM

def jwt_maker():
    jwt_payload = {}
    jwt_header = {'alg': JWT_ALGORITHM, 'typ': 'JWT'}

    token = encode(jwt_payload, JWT_SECRET, algorithm = JWT_ALGORITHM, headers = jwt_header)
    return token

def jwt_verify(token: str):
    try: decode(token, JWT_SECRET, algorithms = [JWT_ALGORITHM])
    except Exception: return False

    return True
