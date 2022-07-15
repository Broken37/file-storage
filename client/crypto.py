import jwt

import constants


def jwt_encode(payload):
    return jwt.encode(payload, constants.SECRET_KEY, algorithm='HS256')


def jwt_decode(token):
    return jwt.decode(token, constants.SECRET_KEY, algorithms='HS256')
