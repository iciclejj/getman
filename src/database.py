from datetime import datetime
import json
import os

from constants import (
        FILE_PATH_DB,
        DIR_PATH_DB,
        )


# TODO: TURN THIS SHIT INTO A CLASS !!!!!!!!!!!!!!!!!!!!!!!!
def init_db(): # overwrite=True
    if not os.path.isdir(DIR_PATH_DB):
        os.mkdir(DIR_PATH_DB)

    db_dict = {
            'created_at': str(datetime.now()),
            'updated_at': str(datetime.now()),
            'packages': {},
            'upgradeable': {}
    }

    overwrite_db(db_dict)

    return FILE_PATH_DB

def get_db_dict():
    with open(FILE_PATH_DB, 'r') as db_file:
        db_dict = json.loads(db_file.read())

    return db_dict

def overwrite_db(db_dict):
    db_json = json.dumps(db_dict)

    with open(FILE_PATH_DB, 'w+') as db_file:
        db_file.write(db_json)

def remove_package_entry(url, include_upgradeable=True):
    db_dict = get_db_dict()

    if db_dict['packages'].get(url) is None:
        print('Package not found in database:')
        print(url, '\n')
        raise KeyError('Package not found in database')

    del db_dict['packages'][url]

    if include_upgradeable:
        db_dict['upgradeable'].pop(url, None)

    overwrite_db(db_dict)

def is_package_url(url):
    packages = get_db_dict()['packages']

    if url in packages:
        return True

    return False

def get_package_attribute(url, attribute):
    db_dict = get_db_dict()
    return db_dict['packages'][url][attribute]

def get_url_from_install_filename(install_filename):
    db_dict = get_db_dict()

    for url, package_metadata in db_dict['packages'].items():
        if package_metadata['install_filename'] == install_filename:
            return url

    return None

if __name__ == '__main__':
    pass

