import os

import command_handlers
from constants import (
        DIR_PATH_PACKAGES,
        )
from gm_argparse import create_parser
from init_getman import init_getman, needs_init

# TODO: implement download cache handler
#       rename DIR_PATH_PACKAGES to DIR_PATH_DOWNLOAD or DIR_PATH_CACHE
def main():
    def _clear_download_directory():
        for filename in os.listdir(DIR_PATH_PACKAGES):
            file_path = os.path.join(DIR_PATH_PACKAGES, filename)

            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f'{file_path} deletion failed during cleanup ({e}).')

    # Parse the command-line arguments
    parser = create_parser()
    args = parser.parse_args()

    if needs_init() and args.command != 'init':
        answer = input('Missing getman files detected. Run initialization?'
                       ' (Will ask before deleting or overwriting files).'
                       ' (y/N): ')

        if answer.lower() in ['y', 'yes']:
            init_getman()

    if needs_init() and args.command != 'init':
        print('Missing required files. Exiting. Nothing has been done.')
        return

    command_handler = getattr(command_handlers, args.command + '_')

    try:
        command_handler(**vars(args))
    finally:
        _clear_download_directory()

if __name__ == '__main__':
    main()

