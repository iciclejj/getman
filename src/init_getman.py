import os
import shutil # for rm -r

import filenames as names
from database import init_db
from config import init_config

def init_getman():
    if not os.path.isdir(names.DATA_DIR_PATH):
        os.makedirs(names.DATA_DIR_PATH)

    if not os.path.isdir(names.CONFIG_DIR_PATH):
        os.makedirs(names.CONFIG_DIR_PATH)

    if not os.path.isdir(names.DEFAULT_DEB_PACKAGE_DIR_PATH):
        os.makedirs(names.DEFAULT_DEB_PACKAGE_DIR_PATH)

    db_path = init_db()
    config_path = init_config(db_path)

# TODO: check for both config and db, and let user decide whether to do a full reset
def needs_init():
    missing_files = []

    if not os.path.isfile(names.CONFIG_FILE_PATH):
        return True

def delete_everything():
    shutil.rmtree(names.CONFIG_DIR_PATH)
    shutil.rmtree(names.DATA_DIR_PATH)

# add check for config files and subdirs
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
        
