import jwt
from django.conf import settings

import random
import string


def get_random_string(length=32):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


def jwt_encode(payload):
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def jwt_decode(token):
    return jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
