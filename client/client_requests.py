import base64
import json

from crypto import jwt_decode, jwt_encode, jwt_sign, rsa_encrypt, rsa_decrypt
from requests import get, post, put, delete
from rsa import PublicKey

import constants


def encode_data_with_hash(data, key):
    payload = {
        'data': data,
        'hash': hash(data)
    }
    return jwt_encode(payload, key)


def decode_data_with_hash(encoded_data, key):
    payload = jwt_decode(encoded_data.encode(), key)
    if hash(payload['data']) != payload['hash']:
        raise ValueError
    return payload['data']


def get_file(token, auth_key, key=None):
    if not key:
        key = jwt_sign(token)
    response = get(
        f"{constants.SERVER_URL}/files/{token}",
        headers={'AUTHORIZATION': auth_key},
    )
    response.raise_for_status()
    encoded_data = response.json().get('data')
    return decode_data_with_hash(encoded_data, key)


def post_file():
    response = post(
        f"{constants.SERVER_URL}/files",
    )
    response.raise_for_status()
    json_response = response.json()
    return json_response['token'], json_response['write_key']


def put_file(token, data, write_key, auth_key, key=None):
    if not key:
        key = jwt_sign(token)
    response = put(
        f"{constants.SERVER_URL}/files/{token}",
        data=dict(data=encode_data_with_hash(data, key), write_key=write_key),
        headers={'AUTHORIZATION': auth_key},
    )
    response.raise_for_status()
    return response.json().get('data')


def delete_file(token, write_key, auth_key):
    response = delete(
        f"{constants.SERVER_URL}/files/{token}",
        headers={'AUTHORIZATION': auth_key},
        data={'write_key': write_key}
    )
    response.raise_for_status()
    return


def get_user_public_key(username):
    response = get(
        f"{constants.SERVER_URL}/users/{username}/public",
    )
    if response.status_code == 404:
        print(f'user with user name {username} not found!')
        return
    return PublicKey.load_pkcs1(response.json()['public_key'].encode())


def encrypt_share(data, user_public_key):
    return base64.b64encode(rsa_encrypt(json.dumps(data), user_public_key)).decode()


def decrypt_share(encrypted_data):
    return json.loads(rsa_decrypt(base64.b64decode(encrypted_data)))

def create_share(token, data, username, auth_key):
    user_public_key = get_user_public_key(username)
    if not user_public_key:
        return
    encoded_data = encrypt_share(data, user_public_key)
    response = post(
        f"{constants.SERVER_URL}/shares",
        data=dict(username=username, token=token, data=encoded_data),
        headers={'AUTHORIZATION': auth_key},
    )


def get_my_shares(auth_key):
    response = get(
        f"{constants.SERVER_URL}/shares",
        headers={'AUTHORIZATION': auth_key},
    )
    result = list()
    print(response.json())
    for token, data in response.json():
        result.append((token, decrypt_share(data)))
    return result
