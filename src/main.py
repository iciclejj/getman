import sys

import command_handlers
import database as db
from gm_argparse import create_parser
from init_getman import init_getman, needs_init
import filenames as names

def main():
    # Parse the command-line arguments
    args = create_parser()

    # Extract the command from the args namespace
    command = args.command

    if command != 'init' and needs_init():
        answer = input('Missing getman files detected. Run initialization?'
                       ' (Will ask before deleting or overwriting files).'
                       ' (y/N): ')

        if answer in ['y', 'Y']:
            init_getman()

        if needs_init():
            print('Missing required files. Exiting. Nothing has been done.')
            return

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
            command_handlers.list_()
        elif command == 'init':
            command_handlers.init(args.purge)
    except Exception as exception: # TODO: HANDE THIS PROPERLY
        print('ERROR:', exception)

if __name__ == '__main__':
    main()

