from datetime import datetime
import json
import os

from constants import (
        FILE_PATH_DB,
        DIR_PATH_DB,
        )

class DB():
    # TODO: more efficient database updating than full overwrite
    #       maybe stop using url as primary key (use no primary key)
    #               do this for both packages and upgradeable
    #       change FILE_NAME_DB (remove default)

    db_path = FILE_PATH_DB
    db_dict = None # this gets initialized only once (see __init__)

    def __init__(self):
        if not os.path.isfile(DB.db_path):
            raise FileNotFoundError(f'{DB.db_path} not found. Try init.')

        if DB.db_dict is None:
            with open(DB.db_path, 'r', encoding='utf-8') as db_file:
                DB.db_dict = json.loads(db_file.read())

    # TODO: .copy()
    def __getitem__(self, key):
        return DB.db_dict[key]

    def __setitem__(self, key, value):
        DB.db_dict[key] = value

    def _overwrite_db(self):
        DB.db_dict['updated_at'] = str(datetime.now())

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

    def add_package_entry(self, url, install_filename, install_path,
                          download_filename, md5_base64, update_only=False):
        curr_time = str(datetime.now())

        created_at = curr_time
        updated_at = curr_time

        if update_only:
            if not self.is_package_url(url):
                raise KeyError(f'{url} not found in packages.')

            created_at = self.get_package_attribute(url, 'created_at')

        package_dict = {
                'created_at': created_at,
                'updated_at': updated_at,
                'install_filename': install_filename,
                'install_path': install_path,
                'download_filename': download_filename,
                'md5_base64': md5_base64,
        }

        DB.db_dict['packages'][url] = package_dict

        self._overwrite_db()

    def add_upgradeable_entry(self, url):
        DB.db_dict['upgradeable'][url] = {}

        self._overwrite_db()

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

    curr_time = str(datetime.now())

    db_dict = {
            'created_at': curr_time,
            'updated_at': curr_time,
            'packages': {},
            'upgradeable': {}
    }

    db_json = json.dumps(db_dict)

    with open(FILE_PATH_DB, 'w+', encoding='utf-8') as db_file:
        db_file.write(db_json)

    return FILE_PATH_DB

if __name__ == '__main__':
    pass

