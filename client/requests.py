from requests import get, post, put, delete

import constants
from commands import auth_key


def get_file(token):
    response = get(
        f"{constants.SERVER_URL}/files/{token}",
        headers={'AUTHORIZATION': auth_key},
    )
    if response.status_code == 200:
        return response.json().get('data')
    return None


def post_file(data):
    response = post(
        f"{constants.SERVER_URL}/files",
        data=dict(data=data),
        headers={'AUTHORIZATION': auth_key},
    )
    if response.status_code == 200:
        return response.json().get('token')
    return None


def put_file(token, data):
    response = put(
        f"{constants.SERVER_URL}/files/{token}",
        data=dict(data=data),
        headers={'AUTHORIZATION': auth_key},
    )
    if response.status_code == 200:
        return response.json().get('data')
    return None


def delete_file(token):
    response = delete(
        f"{constants.SERVER_URL}/files/{token}",
        headers={'AUTHORIZATION': auth_key},
    )
    if response.status_code == 200:
        return response.json().get('data')
    return None
