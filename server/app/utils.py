import time

import bcrypt
from app.models import User
from django.conf import settings
from filesystem.crypto import jwt_decode
from rest_framework.response import Response

salt = b'$2b$12$Ks8v.2.M.l2aQSygyN/EM.'


def get_user(authorization):
    payload = jwt_decode(authorization)
    print(payload)
    if payload['expires'] < time.time():
        return None
    print('got here')
    return User.objects.get(user_name=payload['user_name'])


def need_authorization(func):
    def new_func(cls, request, *args, **kwargs):
        print(request.headers)
        authorization = request.headers.get('Authorization')
        print(authorization)
        if not authorization:
            return Response(status=401)
        user = get_user(authorization)
        if not user:
            return Response(status=401)
        request.user = user
        return func(cls, request, *args, **kwargs)

    return new_func


def get_hashed_pass(raw_password):
    combo_password = raw_password + settings.SECRET_KEY
    hashed_password = bcrypt.hashpw(combo_password.encode(), salt)
    return hashed_password.decode()
