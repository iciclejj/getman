from datetime import datetime
import json
import os

from constants import (
        FILE_NAME_DB_DEFAULT,
        DIR_PATH_DB,
        )

# for testing
import secrets

# TODO: TURN THIS SHIT INTO A CLASS !!!!!!!!!!!!!!!!!!!!!!!!
def init_db(db_name=None, overwrite=True):
    if db_name is None:
        db_name = FILE_NAME_DB_DEFAULT

    if not os.path.isdir(DIR_PATH_DB):
        os.mkdir(DIR_PATH_DB)

    db_path = os.path.join(DIR_PATH_DB, db_name)

    db_dict = {
            'created_at': str(datetime.now()),
            'updated_at': str(datetime.now()),
            'packages': {},
            'upgradeable': {}
    }

    overwrite_db(db_path, db_dict)
    
    return db_path

def get_db_dict(db_name=None):
    # TODO: probably package this boilerplate into a function (do this everywhere)
    #                (possibly remove custom db altogether) 
    #       use get_config to db name when None
    if db_name is None:
        db_name = FILE_NAME_DB_DEFAULT

    db_path = os.path.join(DIR_PATH_DB, db_name)

    with open(db_path, 'r') as db_file:
        db_dict = json.loads(db_file.read())

    return db_dict

# TODO: possibly make db_name argument not need .json (automatically append it)
#               (do this everywhere)
def overwrite_db(db_name, db_dict):
    if db_name is None:
        db_name = FILE_NAME_DB_DEFAULT

    db_path = os.path.join(DIR_PATH_DB, db_name)
    db_json = json.dumps(db_dict)

    # TODO: add try/except
    with open(db_path, 'w+') as db_file:
        db_file.write(db_json)

def remove_package_entry(db_name, url, include_upgradeable=True):
    db_dict = get_db_dict(db_name)

    if db_dict['packages'].get(url) is None:
        print('Package not found in database:')
        print(url, '\n')
        raise KeyError('Package not found in database')

    del db_dict['packages'][url]
    
    if include_upgradeable:
        db_dict['upgradeable'].pop(url, None)

    overwrite_db(db_name, db_dict)

def is_package_url(db_name, url):
    packages = get_db_dict(db_name)['packages']

    if url in packages:
        return True
    else:
        return False

def get_package_attribute(db_name, url, attribute):
    db_dict = get_db_dict(db_name)
    return db_dict['packages'][url][attribute]

def get_url_from_install_filename(db_name, install_filename):
    db_dict = get_db_dict(db_name)

    for url, package_metadata in db_dict['packages'].items():
        if package_metadata['install_filename'] == install_filename:
            return url

    return None

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

