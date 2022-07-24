import hashlib

import jwt
import rsa
from rsa import PrivateKey

import constants

private_key = None


def jwt_encode(payload, key):
    return jwt.encode(payload, key, algorithm='HS256')


def jwt_decode(token, key):
    return jwt.decode(token, key, algorithms='HS256')


def jwt_sign(s, length=16):
    return hashlib.sha256("{}$$${}".format(constants.SECRET_KEY, s).encode()).hexdigest()[:length]


def rsa_encrypt(message, public_key):
    return rsa.encrypt(message.encode(),
                       public_key)


def rsa_decrypt(encMessage):
    if private_key:
        return rsa.decrypt(encMessage, private_key).decode()


def read_private_key(username):
    with open(f'{username}_rsa', 'rb') as file:
        global private_key
        private_key = PrivateKey.load_pkcs1(b''.join(file.readlines()))


def generate_rsa_keys(username):
    global private_key
    public_key, private_key = rsa.newkeys(2048)
    with open(f'{username}_rsa', 'wb') as file:
        file.write(private_key.save_pkcs1())
    return public_key.save_pkcs1().decode()
