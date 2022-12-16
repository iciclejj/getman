import argparse
import sys

import command_handlers
import database as db
from gm_argparse import init_parser
from init_getman import init_getman, needs_init
import filenames as names

def main():
    try:
        command, args, parser = init_parser()
    except Exception as exception:
        print(exception)
        return

    if needs_init():
        init_getman() # TODO: add --force flag for init

    try:
        if command == 'install':
            command_handlers.install(args.url, args.name, args.force)
        elif command == 'uninstall':
            command_handlers.uninstall(args.package, args.url)
        elif command == 'update':
            command_handlers.update()
        elif command == 'upgrade':
            command_handlers.upgrade()
        elif command == 'list':
            command_handlers.list()
        elif command == 'init':
            command_handlers.init()
    except Exception as exception:
        print('ERROR:', exception)

if __name__ == '__main__':
    main()

