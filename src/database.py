from datetime import datetime
import json
import os

from constants import (
        FILE_PATH_DB,
        DIR_PATH_DB,
        )

class PackageDatabase():
    # TODO: more efficient database updating than full overwrite

    def _overwrite_db(self):
        db_json = json.dumps(self.db_dict)

        with open(self.db_path, 'w+', encoding='utf-8') as db_file:
            db_file.write(db_json)

    def __init__(self, db_path=FILE_PATH_DB):
        if not os.path.isfile(db_path):
            raise FileNotFoundError('Package database not found. Try init.')

        with open(db_path, 'r', encoding='utf-8') as db_file:
            self.db_dict = json.loads(db_file.read())

        self.db_path = db_path

    def remove_package_entry(self, url, include_upgradeable=True):
        # TODO: add include_install and allow indexing using install_filename
        #               remove include_upgradeable
        if self.db_dict['packages'].get(url) is None:
            raise KeyError(f'Package not found in database: {url}')

        del db_dict['packages'][url]

        if include_upgradeable:
            db_dict['upgradeable'][url]

        self._overwrite_db(db_dict)

    def is_package_url(self, url):
        if url in self.db_dict['packages']:
            return True

        return False

    def get_package_attribute(self, url, attribute):
        return self.db_dict['packages'][url][attribute]

    def get_url_from_install_filename(self, install_filename):
        for url, package_metadata in self.db_dict['packages']:
            if package_metadata['install_filename'] == install_filename:
                return url

        # TODO: raise KeyError instead
        return None

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

