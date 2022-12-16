import os
import shutil # for rm -r

import filenames as names
from database import init_db
from config import init_config

# TODO: check for both config and db, and let user decide whether to do a full reset
def init_getman():
    print('Initializing getman files and directories in:')
    print(names.DATA_DIR_PATH)
    print(names.CONFIG_DIR_PATH, '\n')

    if not os.path.isdir(names.DATA_DIR_PATH):
        os.makedirs(names.DATA_DIR_PATH)

    if not os.path.isdir(names.CONFIG_DIR_PATH):
        os.makedirs(names.CONFIG_DIR_PATH)

    if not os.path.isdir(names.DEFAULT_DEB_PACKAGE_DIR_PATH):
        os.makedirs(names.DEFAULT_DEB_PACKAGE_DIR_PATH)

    db_path = init_db()
    config_path = init_config(db_path)

    print('getman initialized.')

def needs_init():
    if not os.path.isfile(names.CONFIG_FILE_PATH):
        return True

    with open(names.CONFIG_FILE_PATH) as config_file:
        db_path = json.loads(config_file)['db_path']

    if not os.path.isfile(db_path):
        return True

    return False

def delete_everything():
    shutil.rmtree(names.CONFIG_DIR_PATH)
    shutil.rmtree(names.DATA_DIR_PATH)
    print('getman directories deleted.\n')

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
        
