from datetime import datetime
import json
import os

from constants import (
        FILE_PATH_DB,
        DIR_PATH_DB,
        )

class DB():
    # TODO: more efficient database updating than full overwrite
    #       add __getitem__ instead of db.db_dict['something']

    # Shared db_path and db_dict across all instances
    if not os.path.isfile(FILE_PATH_DB):
        raise FileNotFoundError(f'{FILE_PATH_DB} not found. Try init.')

    db_path = FILE_PATH_DB
    with open(db_path, 'r', encoding='utf-8') as db_file:
        db_dict = json.loads(db_file.read())

    def __init__(self):
        pass

    # TODO: .copy()
    def __getitem__(self, key):
        return DB.db_dict[key]

    def __setitem__(self, key, value):
        DB.db_dict[key] = value

    def _overwrite_db(self):
        db_json = json.dumps(DB.db_dict)

        with open(self.db_path, 'w+', encoding='utf-8') as db_file:
            db_file.write(db_json)

    def remove_package_entry(self, url, include_upgradeable=True):
        # TODO: add include_install and allow indexing using install_filename
        #               remove include_upgradeable
        if DB.db_dict['packages'].get(url) is None:
            raise KeyError(f'Package not found in database: {url}')

        del DB.db_dict['packages'][url]

        if include_upgradeable:
            DB.db_dict['upgradeable'].pop(url, None)

        self._overwrite_db()

    def remove_upgradeable_entry(self, url):
        try:
            del DB.db_dict['upgradeable'][url]
            self._overwrite_db()
        except KeyError as e:
            raise KeyError('upgradeable entry not found') from e

    def get_upgradeable(self):
        return DB.db_dict['upgradeable'] # TODO: add .copy() everywhere

    def get_packages(self):
        return DB.db_dict['packages'] # TODO: add .copy() everywhere

    def is_package_url(self, url):
        if url in DB.db_dict['packages']:
            return True

        return False

    def get_package_attribute(self, url, attribute):
        return DB.db_dict['packages'][url][attribute]

    def get_url_from_install_filename(self, install_filename):
        for url, package_metadata in DB.db_dict['packages'].items():
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

    db_json = json.dumps(db_dict)

    with open(FILE_PATH_DB, 'w+', encoding='utf-8') as db_file:
        db_file.write(db_json)

    return FILE_PATH_DB

if __name__ == '__main__':
    pass

