"""
JWT management.

Generates and Decryptes JWT
"""
import jwt
import os
import time
import random


def generate_jwt(username):
    """
    Generate JWT.

    Creates a jwt given a username
    """
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


def verify_jwt(cookies):
    """
    Verify JWT.

    Checks whether jwt is correct and within time limits
    """
    try:
        token = cookies.get("JWT")
        decoded = jwt.decode(token,
                             os.enviorn.get('JWT_KEY'),
                             algorithms=[os.environ.get('JWT_ALGO')])
        if decoded['exp'] > int(time.time()):
            return None
        return decoded['data']['username']

    except Exception as e:
        return e
