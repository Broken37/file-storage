import json

from requests import post

import constants
from client.models import DirectoryManager
from client.requests import get_file, delete_file, post_file
from models import Directory

cache = dict()
auth_key = None
root_token = None
path = '~'


def find_file(path):
    if path in cache:
        return cache[path]
    if path == '~':
        data = cache.get(path, get_file(root_token))
        cache[path] = data
        return data
    father_path = path[:path.rfind('/')]
    file_name = path[path.rfind('/'):]
    father_file = cache.get(path[:path.rfind('/')], find_file(father_path))
    directory = Directory.from_data(father_file)
    for file in directory:
        if file.name == file_name:
            data = get_file(file.token)
            cache[path] = data
            return file.token, data


def relative_to_absolute(input_path):
    global path
    result = path
    for part in input_path.split('/'):
        if part == '.':
            continue
        if part == '..':
            result = result[:result.rfind('/')]
            continue
        result = f"{result}/{part}"
    return result


def get_file_type(data):
    return json.loads(data)['type']


def rm(input_path, *options):
    absolute_path = input_path if input_path.startswith('~') else relative_to_absolute(input_path)
    if absolute_path == '~':
        print('not allowed')
        return
    token, data = find_file(absolute_path)
    if not data:
        print(f"No such file or directory: {input_path}")
    file_type = get_file_type(data)
    if file_type == 'directory':
        if not '-r' in options:
            print(f'cannot remove {input_path}: Is a directory')
            return
        dir = Directory.from_data(data)
        for item, _ in dir.list:
            rm(f"{input_path}/item", '-r')
    delete_file(token)
    father_path = absolute_path[:absolute_path.rfind('/')]
    father_token, father_data = find_file(father_path)
    dir_manager = DirectoryManager(father_token, father_data)
    dir_manager.remove(token)
    dir_manager.put()


def ls(input_path):
    absolute_path = input_path if input_path.startswith('~') else relative_to_absolute(input_path)
    _, data = find_file(absolute_path)
    if not data:
        print(f"no such file or directory: {input_path}")
    try:
        dir = Directory.from_data(data)
        for item, _ in dir.list:
            print(item)
    except TypeError:
        pass


def mkdir(input_path):
    absolute_path = input_path if input_path.startswith('~') else relative_to_absolute(input_path)
    father_path = absolute_path[:absolute_path.rfind('/')]
    father_token, father_data = find_file(father_path)
    dir_manager = DirectoryManager(father_token, father_data)
    data = json.dumps(dict(list=list(), type='directory'))
    name = absolute_path[absolute_path.rfind('/') + 1:]
    token = post_file(data)
    dir_manager.add(name, token)
    dir_manager.put()


def touch(input_path):
    absolute_path = input_path if input_path.startswith('~') else relative_to_absolute(input_path)
    father_path = absolute_path[:absolute_path.rfind('/')]
    father_token, father_data = find_file(father_path)
    dir_manager = DirectoryManager(father_token, father_data)
    data = json.dumps(dict(data='', type='file'))
    name = absolute_path[absolute_path.rfind('/') + 1:]
    token = post_file(data)
    dir_manager.add(name, token)
    dir_manager.put()


def cd(input_path):
    absolute_path = input_path if input_path.startswith('~') else relative_to_absolute(input_path)
    _, data = find_file(absolute_path)
    if not data:
        print(f"no such file or directory: {input_path}")
        return
    try:
        Directory.from_data(data)
    except TypeError:
        print(f'not a directory: {input_path}')
        return
    global path
    path = absolute_path


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
        global auth_key, root_token
        json_response = response.json()
        auth_key = json_response.get('authorization')
        root_token = json_response.get('root_token')
    else:
        print("login failed")
