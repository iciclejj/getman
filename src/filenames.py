import os

CONFIG_FILE_NAME = 'config.json'
CONFIG_DIR_PATH = os.path.expanduser('~/.config/getman')
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR_PATH, CONFIG_FILE_NAME)

DATA_DIR_PATH = os.path.expanduser('~/.local/share/getman')

DEFAULT_DB_FILE_NAME = 'default_database.json'
DB_DIR_NAME = 'databases'
DB_DIR_PATH = os.path.join(DATA_DIR_PATH, DB_DIR_NAME)
DEFAULT_DB_FILE_PATH = os.path.join(DB_DIR_PATH, DEFAULT_DB_FILE_NAME)

DEFAULT_DEB_PACKAGE_DIR_NAME = 'packages'
DEFAULT_DEB_PACKAGE_DIR_PATH = os.path.join(DATA_DIR_PATH, DEFAULT_DEB_PACKAGE_DIR_NAME)

INSTALL_DIR_PATH = os.path.expanduser('~/.local/bin')
