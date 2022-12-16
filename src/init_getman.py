import json
import os
import shutil # for rm -r

import filenames as names
from database import init_db
from config import init_config

# TODO: check for both config and db, and let user decide
#               whether to do a full reset
def init_getman():
    print('Initializing getman files and directories in:')
    print(names.DATA_DIR_PATH)
    print(names.CONFIG_DIR_PATH)

    if not os.path.isdir(names.DATA_DIR_PATH):
        os.makedirs(names.DATA_DIR_PATH)

    if not os.path.isdir(names.CONFIG_DIR_PATH):
        os.makedirs(names.CONFIG_DIR_PATH)

    if not os.path.isdir(names.DEFAULT_DEB_PACKAGE_DIR_PATH):
        os.makedirs(names.DEFAULT_DEB_PACKAGE_DIR_PATH)

    db_path = names.DEFAULT_DB_FILE_PATH

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
    if not os.path.isfile(names.CONFIG_FILE_PATH):
        config_path = init_config(db_path)
        print(f'Config file created at {config_path}')
    else:
        answer = input(f'Config file already exists as'
                       f' {names.CONFIG_FILE_PATH}. Overwrite? (y/N): ')

        if answer in ['y', 'Y']:
            config_path = init_config(db_path)
            print(f'Config file created at {config_path}')
        else:
            print('Keeping old config file')

    print('getman initialization completed.')

def needs_init():
    if not os.path.isfile(names.CONFIG_FILE_PATH):
        return True

    with open(names.CONFIG_FILE_PATH) as config_file:
        db_dict = json.loads(config_file.read())
        db_path = db_dict['db_path']

    if not os.path.isfile(db_path):
        return True

    return False

def delete_everything():
    shutil.rmtree(names.CONFIG_DIR_PATH)
    shutil.rmtree(names.DATA_DIR_PATH)

# TODO: add check for config files and subdirs
if __name__ == '__main__':
    init_getman()

    if os.path.isdir(names.CONFIG_DIR_PATH):
        print(names.CONFIG_DIR_PATH, 'directory exists')
    else:
        print('ERROR:', names.CONFIG_DIR_PATH, 'directory does not exist')
    
    if os.path.isdir(names.DATA_DIR_PATH):
        print(names.DATA_DIR_PATH, 'directory exists')
    else:
        print('ERROR:', names.DATA_DIR_PATH, 'does not exist')

    print()

    user_input = input('Type DELETE to recursively delete all getman directories\n')

    if user_input == 'DELETE':
        delete_everything()
        
