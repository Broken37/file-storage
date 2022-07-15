from crypto import jwt_decode, jwt_encode
from requests import get, post, put, delete

import constants


def encode_data_with_hash(data):
    payload = {
        'data': data,
        'hash': hash(data)
    }
    return jwt_encode(payload)


def decode_data_with_hash(encoded_data):
    payload = jwt_decode(encoded_data)
    if hash(payload['data']) != payload['hash']:
        raise ValueError
    return jwt_encode(payload)


def get_file(token, auth_key):
    response = get(
        f"{constants.SERVER_URL}/files/{token}",
        headers={'AUTHORIZATION': auth_key},
    )
    response.raise_for_status()
    encoded_data = response.json().get('data')
    return decode_data_with_hash(encoded_data)


def post_file(data, auth_key):
    response = post(
        f"{constants.SERVER_URL}/files",
        data=dict(data=encode_data_with_hash(data)),
        headers={'AUTHORIZATION': auth_key},
    )
    response.raise_for_status()
    return response.json().get('token')


def put_file(token, data, auth_key):
    response = put(
        f"{constants.SERVER_URL}/files/{token}",
        data=dict(data=encode_data_with_hash(data)),
        headers={'AUTHORIZATION': auth_key},
    )
    response.raise_for_status()
    return response.json().get('data')


def delete_file(token, auth_key):
    response = delete(
        f"{constants.SERVER_URL}/files/{token}",
        headers={'AUTHORIZATION': auth_key},
    )
    response.raise_for_status()
    return response.json().get('data')
