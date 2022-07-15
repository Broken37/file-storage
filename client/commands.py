from requests import get, post

from client import constants
from client.models import Directory

cache = dict()
auth_key = None
path = '.'


class Command:
    def __init__(self, chars, function, login_required=False):
        self.chars = chars
        self.function = function
        self.login_required = login_required


def request_file(token):
    token_prefix = 'Bearer '
    response = get(
        f"{constants.SERVER_URL}/files/{token}",
        headers={'AUTHORIZATION': token_prefix + auth_key},
    )
    if response.status_code == 200:
        return response.json().get('data')
    return None


def get_file(path):
    if path == '.':
        pass
    a = path[:path.rfind('/')]
    c = path[path.rfind('/'):]
    b = cache.get(path[:path.rfind('/')], get_file(a))
    dir = Directory.from_data(b)
    for file in dir:
        if file.name == c:
            pass


def list_dir(dir):
    file = get(path)


def signup():
    first_name = input("enter your first name:")
    last_name = input("enter your last name:")
    user_name = input("enter your user name:")
    password = input("enter your password:")
    data = {
        'first_name': first_name,
        'last_name': last_name,
        'user_name': user_name,
        'password': password,
    }
    response = post(f"{constants.SERVER_URL}/signup", data=data)
    if response.status_code == 201:
        print("signup succeeded")
    else:
        print("signup failed")


def login():
    user_name = input("enter your user name:")
    password = input("enter your password:")
    data = {
        'user_name': user_name,
        'password': password,
    }
    response = post(f"{constants.SERVER_URL}/login", data=data)
    if response.status_code == 201:
        print("login succeeded")
        global auth_key
        auth_key = response.json().get('authorization_token')
    else:
        print("login failed")


commands = [
    Command(chars='signup', function=signup),
    Command(chars='login', function=login),
    Command(chars='ls', function=signup),
    Command(chars='touch', function=signup),
    Command(chars='signup', function=signup),
]