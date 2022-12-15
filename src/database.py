from datetime import datetime
import json
import os

import filenames as names

# for testing
import secrets

def init_db(db_name=None, overwrite=True):
    if db_name is None:
        db_name = names.DEFAULT_DB_FILE_NAME

    if not os.path.isdir(names.DB_DIR_PATH):
        os.mkdir(names.DB_DIR_PATH)

    db_path = os.path.join(names.DB_DIR_PATH, db_name)

    db_dict = {
            'created_at': str(datetime.now()),
            'updated_at': str(datetime.now()),
            'packages': {},
            'upgradeable': {}
    }

    overwrite_db(db_path, db_dict)
    
    return db_path

def overwrite_db(db_path, db_dict):
    db_json = json.dumps(db_dict)

    with open(db_path, 'w+') as db_file:
        db_file.write(db_json)
    
if __name__ == '__main__':
    db_dir = os.path.expanduser('~/.local/share/getman')
    db_name = secrets.token_hex(32) + '.json'
    
    while db_name in os.listdir(db_dir):
        db_name = secrets.token_hex(32) + '.json'

    db_path = init_db(db_name, db_dir)

    try:
        with open(db_path, 'r') as json_file:
            db_dict = json.loads(json_file.read())
        print(f'{db_path} successfully created. Now removing.\n')
        print('{db_name} as dict:\n', db_dict)
        os.remove(db_path)
    except:
        print(f'ERROR:\n{download_filepath} was not created.')

