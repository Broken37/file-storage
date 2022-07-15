from commands import auth_key, path

command = None
while command != 'exit':
    command = input(f"path > ")
    if not auth_key:
        print('pls login if you have account or signup if you don\'t')
