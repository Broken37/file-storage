import json
import os

from crypto import read_private_key, generate_rsa_keys, jwt_sign
from requests import post

import constants
from client_requests import get_file, delete_file, post_file, put_file, create_share, get_my_shares

cache = dict()
auth_key = None
root_token = None
root_write_key = None
my_user_name = None
path = '~'


def login_required(func):
    def new_func(*args, **kwargs):
        if not auth_key:
            print('pls login if you have account or signup if you don\'t')
            return
        return func(*args, **kwargs)

    return new_func


def find_key(path):
    file_name = path[path.rfind('/') + 1:]
    father_path = path[:path.rfind('/')]
    dir_manager = DirectoryManager(father_path)
    if dir_manager.has(file_name):
        _, _, _, key = dir_manager.find(file_name)
        return key


def find_file(path, enable_cache=True):
    if path in cache and enable_cache:
        return cache[path]
    if path == '~':
        data = get_file(root_token, auth_key)
        cache[path] = root_token, data, root_write_key
        return root_token, data, root_write_key
    file_name = path[path.rfind('/') + 1:]
    father_path = path[:path.rfind('/')]
    dir_manager = DirectoryManager(father_path)
    for name, token, write_key, key in dir_manager.list:
        if name == file_name:
            data = get_file(token, auth_key, key)
            cache[path] = token, data, write_key
            return token, data, write_key


class DirectoryManager:
    Type = 'directory'

    def add(self, name, token, write_key, key=None):
        if not (name, token, write_key, key) in self.list:
            self.list.append([name, token, write_key, key])

    def remove(self, remove_name, remove_token):
        for name, token, write_key, key in self.list:
            if remove_name == name and remove_token == token:
                self.list.remove([remove_name, remove_token, write_key, key])
                return

    def put(self):
        data = json.dumps(dict(list=self.list, type=self.Type))
        put_file(self.token, data, self.write_key, auth_key)

    def has(self, cname):
        for name, _, _, _ in self.list:
            if name == cname:
                return True
        return False

    def find(self, cname):
        for name, token, write_key, key in self.list:
            if name == cname:
                return name, token, write_key, key

    def __init__(self, path, enable_cache=True):
        self.path = path
        token, data, write_key = find_file(path, enable_cache)
        self.data = json.loads(data)
        if self.data['type'] != self.Type:
            raise TypeError
        self.list = self.data['list']
        self.token = token
        self.write_key = write_key


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
        token, data, write_key = find_file(absolute_path)
    except Exception:
        print(f"No such file or directory: {input_path}")
        return
    if not write_key:
        print(f" you don't have permission to delete this file: {input_path}")
        return
    file_type = get_file_type(data)
    if file_type == 'directory':
        if not '-r' in options:
            print(f'cannot remove {input_path}: Is a directory')
            return
        dir = DirectoryManager(absolute_path)
        for item, _, _, _ in dir.list:
            rm(f"{absolute_path}/{item}", '-r')
    delete_file(token, write_key, auth_key)
    father_path = absolute_path[:absolute_path.rfind('/')]
    name = absolute_path[absolute_path.rfind('/') + 1:]
    dir_manager = DirectoryManager(father_path)
    dir_manager.remove(name, token)
    dir_manager.put()


@login_required
def mv(input_path, output_path):
    absolute_ipath = input_path if input_path.startswith('~') else relative_to_absolute(input_path)
    absolute_opath = input_path if input_path.startswith('~') else relative_to_absolute(output_path)
    token, data, write_key = find_file(absolute_ipath)
    out = find_file(absolute_opath)
    if out and get_file_type(out[1]) != 'directory':
        print('file exists')
        return
    father_ipath = absolute_ipath[:absolute_ipath.rfind('/')]
    father_opath = absolute_opath if out else absolute_opath[:absolute_opath.rfind('/')]
    file_name = absolute_ipath[absolute_ipath.rfind('/') + 1:] if out else absolute_opath[
                                                                           absolute_opath.rfind('/') + 1:]
    odir_manager = DirectoryManager(father_opath)
    odir_manager.add(file_name, token, write_key)
    odir_manager.put()
    idir_manager = DirectoryManager(father_ipath, enable_cache=False)
    name = absolute_ipath[absolute_ipath.rfind('/') + 1:]
    idir_manager.remove(name, token)
    idir_manager.put()


@login_required
def ls(input_path='.'):
    absolute_path = input_path if input_path.startswith('~') else relative_to_absolute(input_path)
    try:
        _, data, _ = find_file(absolute_path)
    except Exception:
        print(f"no such file or directory: {input_path}")
    try:
        dir = DirectoryManager(absolute_path)
        for item, _, _, _ in dir.list:
            print(item)
    except TypeError:
        pass


@login_required
def mkdir(input_path):
    absolute_path = input_path if input_path.startswith('~') else relative_to_absolute(input_path)
    father_path = absolute_path[:absolute_path.rfind('/')]
    dir_manager = DirectoryManager(father_path)
    name = absolute_path[absolute_path.rfind('/') + 1:]
    if dir_manager.has(name):
        print(f'file exists: {name}')
    data = json.dumps(dict(list=list(), type='directory'))
    token, write_key = post_file()
    put_file(token, data, write_key, auth_key)
    dir_manager.add(name, token, write_key)
    dir_manager.put()


@login_required
def touch(input_path):
    absolute_path = input_path if input_path.startswith('~') else relative_to_absolute(input_path)
    father_path = absolute_path[:absolute_path.rfind('/')]
    dir_manager = DirectoryManager(father_path)
    name = absolute_path[absolute_path.rfind('/') + 1:]
    if dir_manager.has(name):
        print('file exists')
        return
    data = json.dumps(dict(data='', type='file'))
    token, write_key = post_file()
    put_file(token, data, write_key, auth_key)
    dir_manager.add(name, token, write_key)
    dir_manager.put()


@login_required
def vim(input_path):
    absolute_path = input_path if input_path.startswith('~') else relative_to_absolute(input_path)
    try:
        token, data, write_key = find_file(absolute_path)
    except Exception:
        print(f"No such file: {input_path}")
        return
    if not write_key:
        print(f" you don't have permission to write on this file: {input_path}")
        return
    file_type = get_file_type(data)
    if file_type == 'directory':
        print(f'cannot edit {input_path}: Is a directory')
        return
    name = absolute_path[absolute_path.rfind('/') + 1:]
    json_data = json.loads(data)
    data = json_data['data']
    with open(name, 'w') as file:
        file.write(data)
    os.system(f'vim {name}')
    with open(name, 'r') as file:
        data = ''.join(file.readlines())
    os.remove(name)
    json_data['data'] = data
    key = find_key(absolute_path)
    put_file(token, json.dumps(json_data), write_key, auth_key, key)


@login_required
def cat(input_path):
    absolute_path = input_path if input_path.startswith('~') else relative_to_absolute(input_path)
    try:
        token, data, write_key = find_file(absolute_path)
    except Exception:
        print(f"No such file: {input_path}")
        return
    file_type = get_file_type(data)
    if file_type == 'directory':
        print(f'cannot cat {input_path}: Is a directory')
        return
    data = json.loads(data)
    print(data['data'])


@login_required
def cd(input_path):
    absolute_path = input_path if input_path.startswith('~') else relative_to_absolute(input_path)
    try:
        _, data, _ = find_file(absolute_path)
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


@login_required
def share(input_path, username, options='-r'):
    absolute_path = input_path if input_path.startswith('~') else relative_to_absolute(input_path)
    token, data, write_key = find_file(absolute_path)
    name = absolute_path[absolute_path.rfind('/') + 1:]
    data = {'token': token, 'key': jwt_sign(token), 'from': my_user_name, 'file_name': name}
    if 'w' in options:
        data['write_key'] = write_key
    create_share(token, data, username, auth_key)


def _fetch_one_share(data):
    cache.clear()
    file_name = data['file_name']
    token = data['token']
    write_key = data.get('write_key')
    key = data['key']
    user_name = data['from']
    dir_path = f'~/shares/{user_name}'
    user_dir = find_file(dir_path)
    if not user_dir:
        mkdir(dir_path)
    cache.clear()
    dir_manager = DirectoryManager(dir_path)
    dir_manager.add(file_name, token, write_key, key)
    dir_manager.put()


@login_required
def fetch_shares():
    share_dir = find_file('~/shares')
    if share_dir:
        rm('~/shares', '-r')
    cache.clear()
    mkdir('~/shares')
    shares = get_my_shares(auth_key)
    print(shares)
    for token, data in shares:
        _fetch_one_share(data)


@login_required
def revoke(input_path):
    absolute_path = input_path if input_path.startswith('~') else relative_to_absolute(input_path)
    token, data, write_key = find_file(absolute_path)
    name = absolute_path[absolute_path.rfind('/') + 1:]
    new_token, new_write_key = post_file()
    put_file(new_token, data, new_write_key, auth_key)
    father_path = absolute_path[:absolute_path.rfind('/')]
    dir_manager = DirectoryManager(father_path)
    dir_manager.remove(name, token)
    dir_manager.add(name, new_token, new_write_key)
    dir_manager.put()
    delete_file(token, write_key, auth_key)


def signup():
    first_name = input("enter your first name: ")
    last_name = input("enter your last name: ")
    user_name = input("enter your user name: ")
    password = input("enter your password: ")
    public_key = generate_rsa_keys(user_name)
    token, write_key = post_file()
    data = {
        'first_name': first_name,
        'last_name': last_name,
        'user_name': user_name,
        'password': password,
        'root_token': token,
        'public_key': public_key
    }
    response = post(f"{constants.SERVER_URL}/signup", data=data)
    global auth_key, root_token, root_write_key, my_user_name
    json_response = response.json()
    auth_key = json_response.get('authorization')
    root_token = json_response.get('root_token')
    root_write_key = write_key
    data = json.dumps(dict(list=list(), type='directory'))
    put_file(token, data, write_key, auth_key)
    my_user_name = user_name
    if response.status_code == 200:
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
        global auth_key, root_token, root_write_key, my_user_name
        json_response = response.json()
        auth_key = json_response.get('authorization')
        root_token = json_response.get('root_token')
        root_write_key = json_response.get('root_write_key')
        read_private_key(user_name)
        my_user_name = user_name
    else:
        print("login failed")


def logout():
    global auth_key, root_token, root_write_key, my_user_name
    auth_key = None
    root_token = None
    root_write_key = None
    my_user_name = None
    print("logout succeeded")


def do_nothing():
    pass


def help_function():
    print('these commands are available')
    for key, value in defined_commands.items():
        print(key)


defined_commands = {
    'cd': cd,
    'ls': ls,
    'mkdir': mkdir,
    'rm': rm,
    'mv': mv,
    'touch': touch,
    'signup': signup,
    'login': login,
    'logout': logout,
    'exit': do_nothing,
    'vim': vim,
    'share': share,
    'revoke': revoke,
    'cat': cat,
    'fetch': fetch_shares,
    'help': help_function,
}
