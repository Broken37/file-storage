from requests import post

auth_key = None



command = None
while command != 'exit':
    command = input()
    if not auth_key:

        commands = input('pls login if you have account or signup if you don\'t')
