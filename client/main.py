from commands import path, defined_commands

command = None
while command != 'exit':
    inputs = input(f"{path} > ").split()
    command = inputs[0]
    if command in defined_commands:
        defined_commands[command](*inputs[1:])
