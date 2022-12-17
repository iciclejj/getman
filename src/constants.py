import os

# DIRECTORIES

DIR_PATH_DATA = os.path.expanduser('~/.local/share/getman')

DIR_PATH_INSTALL = os.path.expanduser('~/.local/bin')

DIR_NAME_DB = 'databases'
DIR_PATH_DB = os.path.join(DIR_PATH_DATA, DIR_NAME_DB)

DIR_NAME_PACKAGES_DEFAULT = 'packages'
DIR_PATH_PACKAGES_DEFAULT = os.path.join(DIR_PATH_DATA, DIR_NAME_PACKAGES_DEFAULT)

DIR_PATH_CONFIG = os.path.expanduser('~/.config/getman')

# FILES

FILE_NAME_DB_DEFAULT = 'default_database.json'
FILE_PATH_DB_DEFAULT = os.path.join(DIR_PATH_DB, FILE_NAME_DB_DEFAULT)

FILE_NAME_CONFIG = 'config.json'
FILE_PATH_CONFIG = os.path.join(DIR_PATH_CONFIG, FILE_NAME_CONFIG)

if __name__ == '__main__':
    print('DIR_PATH_DATA: {DIR_PATH_DATA}')
    print('DIR_PATH_INSTALL: {DIR_PATH_INSTALL}')
    print('DIR_NAME_DB: {DIR_NAME_DB}')
    print('DIR_PATH_DB: {DIR_PATH_DB}')
    print('DIR_NAME_PACKAGES_DEFAULT: {DIR_NAME_PACKAGES_DEFAULT}')
    print('DIR_PATH_PACKAGES_DEFAULT: {DIR_PATH_PACKAGES_DEFAULT}')
    print('DIR_PATH_CONFIG: {DIR_PATH_CONFIG}')

    print('FILE_NAME_DB_DEFAULT: {FILE_NAME_DB_DEFAULT}')
    print('FILE_PATH_DB_DEFAULT: {FILE_PATH_DB_DEFAULT}')
    print('FILE_NAME_CONFIG: {FILE_NAME_CONFIG}')
    print('FILE_PATH_CONFIG: {FILE_PATH_CONFIG}')
