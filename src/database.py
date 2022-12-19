from datetime import datetime
import json
import os

from constants import (
        FILE_PATH_DB,
        DIR_PATH_DB,
        )

class PackageDatabase():
    # TODO: more efficient database updating than full overwrite
    #       add __getitem__ instead of db.db_dict['something']

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

    def __getitem__(self, key):
        return self.db_dict[key]

    def remove_package_entry(self, url, include_upgradeable=True):
        # TODO: add include_install and allow indexing using install_filename
        #               remove include_upgradeable
        if self.db_dict['packages'].get(url) is None:
            raise KeyError(f'Package not found in database: {url}')

        del self.db_dict['packages'][url]

        if include_upgradeable:
            self.db_dict['upgradeable'].pop(url, None)

        self._overwrite_db()

    def is_package_url(self, url):
        if url in self.db_dict['packages']:
            return True

        return False

    def get_package_attribute(self, url, attribute):
        return self.db_dict['packages'][url][attribute]

    def get_url_from_install_filename(self, install_filename):
        for url, package_metadata in self.db_dict['packages'].items():
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

if __name__ == '__main__':
    pass

