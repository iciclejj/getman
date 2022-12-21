from copy import deepcopy
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

    db_path = FILE_PATH_DB
    db_dict = None # this gets initialized only once (see __init__)

    def __init__(self):
        if not os.path.isfile(DB.db_path):
            raise FileNotFoundError(f'{DB.db_path} not found. Try init.')

        if DB.db_dict is None:
            with open(DB.db_path, 'r', encoding='utf-8') as db_file:
                DB.db_dict = json.loads(db_file.read())

    def __getitem__(self, key):
        return DB.db_dict[key]

    def __setitem__(self, key, value):
        DB.db_dict[key] = value

    def _overwrite_db(self):
        DB.db_dict['updated_at'] = str(datetime.now())

        db_json = json.dumps(DB.db_dict)

        with open(self.db_path, 'w+', encoding='utf-8') as db_file:
            db_file.write(db_json)

    def remove_package_entry(self, url=None, pkg_name=None,
                             include_upgradeable=True):
        if url is None and pkg_name is None:
            raise TypeError('Must provide url or pkg_name')

        if url is not None and pkg_name is not None:
            raise TypeError('Can\'t provide both url and pkg_name')

        if pkg_name is not None:
            url = self.get_url_from_pkg_name(pkg_name)

        if DB.db_dict['packages'].get(url) is None:
            raise KeyError(f'Package not found in database: {url}')

        del DB.db_dict['packages'][url]

        if include_upgradeable:
            DB.db_dict['upgradeable'].pop(url, None)

        self._overwrite_db()

    def remove_upgradeable_entry(self, url):
        upgradeable = self.get_upgradeable(deepcopy_=False)

        if upgradeable.get(url) is None:
            raise KeyError('upgradeable entry not found')

        del upgradeable[url]

        self._overwrite_db()

    def add_package_entry(self, url, name, install_path, download_filename,
                          md5_base64, update_only=False):
        curr_time = str(datetime.now())

        created_at = curr_time
        updated_at = curr_time

        if update_only:
            if not self.is_package_url(url):
                raise KeyError(f'{url} not found in packages.')

            created_at = self.get_package_attribute(url, 'created_at',
                                                    deepcopy_=False)

        package_dict = {
                'created_at': created_at,
                'updated_at': updated_at,
                'name': name,
                'install_path': install_path,
                'download_filename': download_filename,
                'md5_base64': md5_base64,
        }

        DB.db_dict['packages'][url] = package_dict

        self._overwrite_db()

    def add_upgradeable_entry(self, url):
        upgradeable = self.get_upgradeable(deepcopy_=False)
        upgradeable[url] = {}

        self._overwrite_db()

    def get_upgradeable(self, deepcopy_=True):
        if deepcopy_:
            return deepcopy(DB.db_dict['upgradeable'])

        return DB.db_dict['upgradeable']

    def get_packages(self, deepcopy_=True):
        if deepcopy_:
            return deepcopy(DB.db_dict['packages'])

        return DB.db_dict['packages']

    def is_package_url(self, url):
        if url in DB.db_dict['packages']:
            return True

        return False

    def get_package_attribute(self, url, attribute, deepcopy_=True):
        packages = self.get_packages(deepcopy_=False)

        if deepcopy_:
            return deepcopy(packages[url][attribute])

        return packages[url][attribute]

    def get_url_from_pkg_name(self, pkg_name):
        packages = self.get_packages()

        for url, package_metadata in packages.items():
            if package_metadata['name'] == pkg_name:
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

