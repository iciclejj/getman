import json
import os
import shutil # for rm -r

from constants import (
        DIR_PATH_CONFIG,
        DIR_PATH_DATA,
        DIR_PATH_PACKAGES_DEFAULT,
        DIR_PATH_DATA,
        DIR_PATH_CONFIG,
        FILE_PATH_DB_DEFAULT,
        FILE_PATH_CONFIG,
        )

from database import init_db
from config import init_config

def init_getman():
    print('Initializing getman files and directories in:')
    print(DIR_PATH_DATA)
    print(DIR_PATH_CONFIG)

    if not os.path.isdir(DIR_PATH_DATA):
        os.makedirs(DIR_PATH_DATA)

    if not os.path.isdir(DIR_PATH_CONFIG):
        os.makedirs(DIR_PATH_CONFIG)

    if not os.path.isdir(DIR_PATH_PACKAGES_DEFAULT):
        os.makedirs(DIR_PATH_PACKAGES_DEFAULT)

    db_path = FILE_PATH_DB_DEFAULT

    # feel like there's a way to clean this up
    if not os.path.isfile(db_path):
        db_path = init_db()
        print(f'Database file created at {db_path}')
    else:
        answer = input(f'Default database file already exists at {db_path}.'
                       f' Overwrite? (y/N): ')

        if answer in ['y', 'Y']:
            db_path = init_db()
            print(f'Database file created at {db_path}')
        else:
            print('Keeping old database file.')

    # feel like there's a way to clean this up
    if not os.path.isfile(FILE_PATH_CONFIG):
        config_path = init_config(db_path)
        print(f'Config file created at {config_path}')
    else:
        answer = input(f'Config file already exists as'
                       f' {FILE_PATH_CONFIG}. Overwrite? (y/N): ')

        if answer in ['y', 'Y']:
            config_path = init_config(db_path)
            print(f'Config file created at {config_path}')
        else:
            print('Keeping old config file')

    print('getman initialization completed.')

def needs_init():
    if not os.path.isfile(FILE_PATH_CONFIG):
        return True

    with open(FILE_PATH_CONFIG) as config_file:
        db_dict = json.loads(config_file.read())
        db_path = db_dict['db_path']

    if not os.path.isfile(db_path):
        return True

    return False

def delete_everything():
    shutil.rmtree(DIR_PATH_CONFIG)
    shutil.rmtree(DIR_PATH_DATA)

# TODO: add check for config files and subdirs
if __name__ == '__main__':
    init_getman()

    if os.path.isdir(DIR_PATH_CONFIG):
        print(DIR_PATH_CONFIG, 'directory exists')
    else:
        print('ERROR:', DIR_PATH_CONFIG, 'directory does not exist')
    
    if os.path.isdir(DIR_PATH_DATA):
        print(DIR_PATH_DATA, 'directory exists')
    else:
        print('ERROR:', DIR_PATH_DATA, 'does not exist')

    print()

    user_input = input('Type DELETE to recursively delete all getman directories\n')

    if user_input == 'DELETE':
        delete_everything()
        
