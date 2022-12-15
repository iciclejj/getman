import argparse
import sys

import command_handlers
import database as db
from gm_argparse import init_parser
from init_getman import init_getman, needs_init

def main():
    try:
        command, args, parser = init_parser()
    except Exception as exception:
        print(exception)
        return

    args = parser.parse_args(args=sys.argv[2:])

    if needs_init():
        init_getman()

    try:
        if command == 'install':
            command_handlers.install(args.url)
        elif command == 'update':
            command_handlers.update()
        elif command == 'init':
            return
    except Exception as exception:
        print('ERROR:', exception)

if __name__ == '__main__':
    main()

