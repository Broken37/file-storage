import time
from getpass import getpass

import bcrypt
from app.models import User
from filesystem.crypto import jwt_decode
from rest_framework.response import Response

master_secret_key = getpass('tell me the master secret key you are going to use')
salt = bcrypt.gensalt()


def get_user(authorization):
    payload = jwt_decode(authorization)
    if payload['expires'] > time.time():
        return None
    return User.objects.get(user_name=payload['user_name'])


def need_authorization(func):
    def new_func(request, *args, **kwargs):
        authorization = request.headers.get('AUTHORIZATION')
        if not authorization:
            return Response(status=401)
        user = get_user(authorization)
        if not user:
            return Response(status=401)
        request.user = user
        return func(request, *args, **kwargs)

    return new_func


def get_hashed_pass(raw_password):
    combo_password = raw_password + salt + master_secret_key
    hashed_password = bcrypt.hashpw(combo_password, salt)
    return hashed_password
