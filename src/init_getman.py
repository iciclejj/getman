# built-in libraries
from os import makedirs
from os.path import isdir, isfile
import shutil # for rm -r

# getman modules
from config import init_config
from constants import (
        DIR_PATH_CONFIG,
        DIR_PATH_DATA,
        DIR_PATH_DOWNLOADS,
        FILE_PATH_DB,
        FILE_PATH_CONFIG,
        )
from database import init_db
import user_input

_GETMAN_REQUIRED_DIR_PATHS = [
        DIR_PATH_CONFIG,
        DIR_PATH_DATA,
        DIR_PATH_DOWNLOADS,
        ]
_GETMAN_REQUIRED_FILE_PATHS = [
        FILE_PATH_CONFIG,
        FILE_PATH_DB,
        ]

def init_getman():
    def _create_dir_if_not_exists(path):
        if not isdir(path):
            makedirs(path)

    def _create_or_prompt_overwrite_file(path, fn_create_file):
        if not isfile(path):
            fn_create_file()
            print(f'{path} created...')
            return

        overwrite = user_input.prompt_yes_no(
                f'{path} already exists. Overwrite?',
                default=False)

        if overwrite:
            fn_create_file()
            print('Overwriting file...')
            return

        print('Keeping old file...')

    # print top-level getman directories
    print('Initializing getman files and directories in:',
           DIR_PATH_DATA,
           DIR_PATH_CONFIG,
           sep='\n')

    for dir_path in _GETMAN_REQUIRED_DIR_PATHS:
        _create_dir_if_not_exists(dir_path)

    _create_or_prompt_overwrite_file(FILE_PATH_CONFIG, init_config)
    _create_or_prompt_overwrite_file(FILE_PATH_DB, init_db)

    print('getman initialization completed.')

def needs_init():
    for dir_path in _GETMAN_REQUIRED_DIR_PATHS:
        if not isdir(dir_path):
            return True

    for file_path in _GETMAN_REQUIRED_FILE_PATHS:
        if not isfile(file_path):
            return True

    return False

def delete_everything():
    for dir_path in _GETMAN_REQUIRED_DIR_PATHS:
        if isdir(dir_path):
            shutil.rmtree(dir_path)

