"""
JWT management.

Generates and Decryptes JWT
"""
import jwt
import os
import time
import random
from backend.types.errors import JWTError


def generate_jwt(username):
    """
    Generate JWT.

    Creates a jwt given a username
    """
    try:
        choice_string = ('0123456789ABCDEFGHIJKLMNOP'
                         'QRSTUVWXYZabcdefghijklmnopqrstuvwxyz~!@#$%^_-')
        rnd = ''.join(random.choice(choice_string) for i in range(24))
        now = int(time.time())
        return jwt.encode({
            'iat': now,
            'nbf': now,
            'exp': now + int(os.environ.get('JWT_TIMEOUT')),
            'jti': rnd,
            'iss': os.environ.get('JWT_ISS'),
            'data': {'username': username}
        }, os.environ.get('JWT_KEY'), algorithm=os.environ.get('JWT_ALGO'))

    except Exception as e:
        raise JWTError(str(e))


def verify_jwt(token):
    """
    Verify JWT.

    Checks whether jwt is correct and within time limits
    """
    try:
        decoded = jwt.decode(token,
                             os.environ.get('JWT_KEY'),
                             algorithms=[os.environ.get('JWT_ALGO')])
        return decoded['data']['username']

    except Exception as e:
        print(type(e))
        if isinstance(e, jwt.exceptions.ExpiredSignatureError):
            raise JWTError(str(e), True)
        raise JWTError(str(e), False)
