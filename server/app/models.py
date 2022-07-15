import time

from crypto import get_random_string
from django.db import models
from filesystem.crypto import jwt_encode


class User(models.Model):
    AUTH_TOKEN_EXPIRATION_TIME = 7 * 24 * 60 * 60  # one week
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    user_name = models.CharField(max_length=32, unique=True)
    password = models.CharField(max_length=128)
    root_key = models.CharField(max_length=32, default=get_random_string)

    def get_authorization(self):
        payload = dict(
            id=self.pk,
            user_name=self.user_name,
            expires=int(time.time() + User.AUTH_TOKEN_EXPIRATION_TIME)
        )
        return jwt_encode(payload)


class File(models.Model):
    key = models.CharField(max_length=32, default=get_random_string, unique=True)
    data = models.TextField()
