import os
import sys

from commands import defined_commands, cache

hashseed = os.getenv('PYTHONHASHSEED')
if not hashseed:
    os.environ['PYTHONHASHSEED'] = '0'
    os.execv(sys.executable, [sys.executable] + sys.argv)

command = None
while command != 'exit':
    cache.clear()
    from commands import path
    inputs = input(f"{path} > ").split()
    command = inputs[0]
    if command in defined_commands:
        defined_commands[command](*inputs[1:])
