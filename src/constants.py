import os

CONFIG_FILE_NAME = 'config.json'
CONFIG_DIR_PATH = os.path.expanduser('~/.config/getman')
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR_PATH, CONFIG_FILE_NAME)

DATA_DIR_PATH = os.path.expanduser('~/.local/share/getman')

DEFAULT_DB_FILE_NAME = 'default_database.json'
DB_DIR_NAME = 'databases'
DB_DIR_PATH = os.path.join(DATA_DIR_PATH, DB_DIR_NAME)
DEFAULT_DB_FILE_PATH = os.path.join(DB_DIR_PATH, DEFAULT_DB_FILE_NAME)

DEFAULT_PACKAGE_DIR_NAME = 'packages'
DEFAULT_PACKAGE_DIR_PATH = os.path.join(DATA_DIR_PATH, DEFAULT_PACKAGE_DIR_NAME)

INSTALL_DIR_PATH = os.path.expanduser('~/.local/bin')

if __name__ == '__main__':
    print(f'CONFIG_FILE_NAME: {CONFIG_FILE_NAME}')
    print(f'CONFIG_DIR_PATH: {CONFIG_DIR_PATH}')
    print(f'CONFIG_FILE_PATH: {CONFIG_FILE_PATH}')
    print(f'DATA_DIR_PATH: {DATA_DIR_PATH}')
    print(f'DEFAULT_DB_FILE_NAME: {DEFAULT_DB_FILE_NAME}')
    print(f'DB_DIR_NAME: {DB_DIR_NAME}')
    print(f'DB_DIR_PATH: {DB_DIR_PATH}')
    print(f'DEFAULT_DB_FILE_PATH: {DEFAULT_DB_FILE_PATH}')
    print(f'DEFAULT_PACKAGE_DIR_NAME: {DEFAULT_PACKAGE_DIR_NAME}')
    print(f'DEFAULT_PACKAGE_DIR_PATH: {DEFAULT_PACKAGE_DIR_PATH}')
    print(f'INSTALL_DIR_PATH: {INSTALL_DIR_PATH}')
