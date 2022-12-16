import sys

import command_handlers
import database as db
from gm_argparse import create_parser
from init_getman import init_getman, needs_init
import filenames as names

def main():
    # Parse the command-line arguments
    parser = create_parser()
    args = parser.parse_args()

    if needs_init() and command != 'init':
        answer = input('Missing getman files detected. Run initialization?'
                       ' (Will ask before deleting or overwriting files).'
                       ' (y/N): ')

        if answer in ['y', 'Y']:
            init_getman()

    if needs_init() and command != 'init':
        print('Missing required files. Exiting. Nothing has been done.')
        return

    command_handler = getattr(command_handlers, args.command + '_') 
    command_handler(**vars(args))

if __name__ == '__main__':
    main()

