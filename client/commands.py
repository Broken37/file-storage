import json

from requests import post

import constants
from client_requests import get_file, delete_file, post_file, put_file

cache = dict()
auth_key = None
root_token = None
path = '~'


def login_required(func):
    def new_func(*args, **kwargs):
        if not auth_key:
            print('pls login if you have account or signup if you don\'t')
            return
        return func(*args, **kwargs)

    return new_func


def find_file(path):
    if path in cache:
        return cache[path]
    if path == '~':
        _, data = cache.get(path, (root_token, get_file(root_token, auth_key)))
        cache[path] = root_token, data
        return root_token, data
    file_name = path[path.rfind('/') + 1:]
    father_path = path[:path.rfind('/')]
    dir_manager = DirectoryManager(father_path)
    for name, token in dir_manager.list:
        if name == file_name:
            data = get_file(token, auth_key)
            cache[path] = token, data
            return token, data


class DirectoryManager:
    Type = 'directory'

    def add(self, name, token):
        if not (name, token) in self.list:
            self.list.append([name, token])

    def remove(self, remove_token):
        remove_name = None
        print(self.list)
        print(remove_token)
        for name, token in self.list:
            if remove_token == token:
                remove_name = name
        if remove_name:
            print(self.list)
            print((remove_name, remove_token))
            self.list.remove([remove_name, remove_token])

    def put(self):
        data = json.dumps(dict(list=self.list, type=self.Type))
        put_file(self.token, data, auth_key)

    def __init__(self, path):
        self.path = path
        token, data = find_file(path)
        self.data = json.loads(data)
        if self.data['type'] != self.Type:
            raise TypeError
        self.list = self.data['list']
        self.token = token


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


@login_required
def rm(input_path, *options):
    absolute_path = input_path if input_path.startswith('~') else relative_to_absolute(input_path)
    if absolute_path == '~':
        print('not allowed')
        return
    try:
        token, data = find_file(absolute_path)
    except Exception:
        print(f"No such file or directory: {input_path}")
        return
    file_type = get_file_type(data)
    if file_type == 'directory':
        if not '-r' in options:
            print(f'cannot remove {input_path}: Is a directory')
            return
        dir = DirectoryManager(absolute_path)
        for item, _ in dir.list:
            rm(f"{absolute_path}/item", '-r')
    delete_file(token, auth_key)
    father_path = absolute_path[:absolute_path.rfind('/')]
    dir_manager = DirectoryManager(father_path)
    dir_manager.remove(token)
    dir_manager.put()


@login_required
def mv(input_path, output_path):
    absolute_ipath = input_path if input_path.startswith('~') else relative_to_absolute(input_path)
    absolute_opath = input_path if input_path.startswith('~') else relative_to_absolute(output_path)
    token, data = find_file(absolute_ipath)
    out = find_file(absolute_opath)
    if out and get_file_type(out[1]) != 'directory':
        print('file exists')
        return
    father_ipath = absolute_ipath[:absolute_ipath.rfind('/')]
    father_opath = absolute_opath if out else absolute_opath[:absolute_opath.rfind('/')]
    file_name = absolute_ipath[absolute_ipath.rfind('/') + 1:] if out else absolute_opath[
                                                                           absolute_opath.rfind('/') + 1:]
    odir_manager = DirectoryManager(father_opath)
    odir_manager.add(file_name, token)
    odir_manager.put()
    idir_manager = DirectoryManager(father_ipath)
    idir_manager.remove(token)
    idir_manager.put()


@login_required
def ls(input_path='.'):
    absolute_path = input_path if input_path.startswith('~') else relative_to_absolute(input_path)
    try:
        _, data = find_file(absolute_path)
    except Exception:
        print(f"no such file or directory: {input_path}")
    try:
        dir = DirectoryManager(absolute_path)
        for item, _ in dir.list:
            print(item)
    except TypeError:
        pass


@login_required
def mkdir(input_path):
    absolute_path = input_path if input_path.startswith('~') else relative_to_absolute(input_path)
    father_path = absolute_path[:absolute_path.rfind('/')]
    dir_manager = DirectoryManager(father_path)
    data = json.dumps(dict(list=list(), type='directory'))
    name = absolute_path[absolute_path.rfind('/') + 1:]
    token = post_file(data, auth_key)
    dir_manager.add(name, token)
    dir_manager.put()


@login_required
def touch(input_path):
    absolute_path = input_path if input_path.startswith('~') else relative_to_absolute(input_path)
    father_path = absolute_path[:absolute_path.rfind('/')]
    dir_manager = DirectoryManager(father_path)
    data = json.dumps(dict(data='', type='file'))
    name = absolute_path[absolute_path.rfind('/') + 1:]
    token = post_file(data, auth_key)
    dir_manager.add(name, token)
    dir_manager.put()


@login_required
def cd(input_path):
    absolute_path = input_path if input_path.startswith('~') else relative_to_absolute(input_path)
    try:
        _, data = find_file(absolute_path)
    except Exception:
        print(f"no such file or directory: {input_path}")
        return
    try:
        DirectoryManager(absolute_path)
    except TypeError:
        print(f'not a directory: {input_path}')
        return
    global path
    path = absolute_path


def signup():
    first_name = input("enter your first name: ")
    last_name = input("enter your last name: ")
    user_name = input("enter your user name: ")
    password = input("enter your password: ")

    data = json.dumps(dict(list=list(), type='directory'))
    token = post_file(data, auth_key)
    data = {
        'first_name': first_name,
        'last_name': last_name,
        'user_name': user_name,
        'password': password,
        'root_token': token
    }
    response = post(f"{constants.SERVER_URL}/signup", data=data)
    if response.status_code == 201:
        print("signup succeeded")
    else:
        print("signup failed")


def login():
    user_name = input("enter your user name: ")
    password = input("enter your password: ")
    data = {
        'user_name': user_name,
        'password': password,
    }
    response = post(f"{constants.SERVER_URL}/login", data=data)
    if response.status_code == 200:
        print("login succeeded")
        global auth_key, root_token
        json_response = response.json()
        auth_key = json_response.get('authorization')
        root_token = json_response.get('root_token')
    else:
        print("login failed")


def do_nothing():
    pass


defined_commands = {
    'cd': cd,
    'ls': ls,
    'mkdir': mkdir,
    'rm': rm,
    'mv': mv,
    'touch': touch,
    'signup': signup,
    'login': login,
    'exit': do_nothing,
}
