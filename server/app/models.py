import time

from django.db import models
from filesystem.crypto import jwt_encode, get_random_string


class User(models.Model):
    AUTH_TOKEN_EXPIRATION_TIME = 7 * 24 * 60 * 60  # one week
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    user_name = models.CharField(max_length=32, unique=True)
    password = models.CharField(max_length=128)
    root_token = models.CharField(max_length=32, default=get_random_string)
    public_key = models.TextField()

    def get_authorization(self):
        payload = dict(
            id=self.pk,
            user_name=self.user_name,
            expires=int(time.time() + User.AUTH_TOKEN_EXPIRATION_TIME)
        )
        return jwt_encode(payload)


class File(models.Model):
    token = models.CharField(max_length=32, default=get_random_string, unique=True, primary_key=True)
    write_key = models.CharField(max_length=32, default=get_random_string)
    data = models.TextField(null=True)


class Share(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.TextField()
