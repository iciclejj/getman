# python standard libraries
import hashlib
import os
import urllib.request
import pathlib
import stat # for chmod +x
from base64 import b64encode
from datetime import datetime
import ssl # fix [SSL: CERTIFICATE_VERIFY_FAILED] error on some devices

# pip libraries
import magic
import certifi # fix [SSL: CERTIFICATE_VERIFY_FAILED] error on some devices

# local modules
from constants import (
        DIR_PATH_INSTALL,
        DIR_PATH_DATA,
        DIR_PATH_CONFIG,
        DIR_PATH_PACKAGES,
        )

import database as db
import init_getman

# TODO: create separate .py files for each command
#               and turn this into an "interface" file

# must match SUPPORTED_CONTENT_TYPE_FIRSTS with startswith
#         (text after '/' is excluded from this list)
SUPPORTED_CONTENT_TYPE_FIRSTS = ['application']
SUPPORTED_FILETYPES = ['application/x-pie-executable']

# fix [SSL: CERTIFICATE_VERIFY_FAILED] error on some devices
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
ssl._create_default_https_context = lambda: SSL_CONTEXT

# TODO:
#
#       EXPERIMENTAL TODOS:
#       auto-detect system/architecture
#       auto-detect site-specific preferred download urls
#               (for example from git repo)
#       use api when supported (for example api.github.com)
def install_(url, install_filename=None, force=False, command=None):
    db_dict = db.get_db_dict()

    # download file and metadata
    # headers is an EmailMessage => returns None if key not found
    headers = _get_headers(url)

    download_filename = headers.get_filename()
    content_type_first = headers['content-type'].partition('/')[0]

    if download_filename is None:
        if install_filename is None:
            print('Could not determine download filename.'
                  ' Please provide custom name with --name')
            return

        download_filename = install_filename
        print('NB: could not determine download_filename.'
              ' Using provided custom program name.')

    # TODO: resolve new install_filename for same url when force == True
    if not force and url in db_dict['packages']:
        install_filename_curr = db_dict['packages'][url]['install_filename']
        print(f'Package already in database as {install_filename_curr}.'
               ' Use -f or --force to force install.')
        return

    # a bit useless in its current state
    # TODO: proper warning
    if content_type_first not in SUPPORTED_CONTENT_TYPE_FIRSTS:
        print('Warning: could not determine if correct filetype before'
              ' downloading. Will check again after download.')

    # downloads file to download_path
    download_path = os.path.join(DIR_PATH_PACKAGES, download_filename)
    urllib.request.urlretrieve(url, filename=download_path)

    # install file
    filetype = magic.from_file(download_path, mime=True)

    if install_filename is None:
        install_filename = pathlib.Path(download_path).stem

    install_path = os.path.join(DIR_PATH_INSTALL, install_filename)

    # TODO: maybe make a general error handler for the install command
    if filetype not in SUPPORTED_FILETYPES:
        os.remove(download_path)
        raise ValueError(f'Unsupported filetype: {filetype}')

    # TODO: make this less hard-coded
    try:
        if filetype == 'application/x-pie-executable':
            file_st = os.stat(download_path)
            plus_x_mode = (file_st.st_mode | stat.S_IXUSR | stat.S_IXGRP
                           | stat.S_IXOTH)
            os.chmod(download_path, plus_x_mode)
            os.replace(download_path, install_path)
    except Exception  as e: # TODO: HANDLE THIS PROPERLY !!!
        os.remove(download_path)
        print(e)
        print('Run with sudo (\'sudo -E\''
              ' if running getman as a python script)')
        return

    content_md5 = _get_base64_md5(install_path)

    db_dict['packages'][url] = {
            'created_at': str(datetime.now()),
            'updated_at': str(datetime.now()),
            'install_filename': install_filename,
            'install_path': install_path,
            'download_filename': download_filename,
            'md5_base64': content_md5,
    }

    db.overwrite_db(db_dict)

    print(f'{install_filename} successfully installed to {install_path}')

def update_(command=None):
    db_dict = db.get_db_dict()

    for url, package_metadata in db_dict['packages'].items():
        headers = _get_headers(url)
        # TODO: maybe rename content_md5 to md5_base64 (everywhere)
        content_md5 = headers['content-md5']

        if content_md5 is None:
            print('Warning: not something isn\'t implemented yet'
                  ', skipping package Xd')
            continue

        if content_md5 != package_metadata['md5_base64']:
            db_dict['upgradeable'][url] = {}

    db.overwrite_db(db_dict)

    upgradeable = db.get_db_dict()['upgradeable']
    n_upgradeable = len(upgradeable)

    print(f'Update successful. Upgradeable packages: {n_upgradeable}')

def upgrade_(command=None):
    upgradeable = db.get_db_dict()['upgradeable']

    n_upgraded = 0

    # TODO: try/except
    #       show total GB before upgrade (in install too)
    #       progress bar (in install too)
    #       probably make a separate upgrade uninstaller
    for url in list(upgradeable.keys()): # list to allow delete as we go
        install_filename = db.get_package_attribute(url, 'install_filename')
        install(url, install_filename, force=True)
        del upgradeable[url]
        n_upgraded += 1

    # reload db_dict after modification by install
    #         (REMOVE IF IMPLEMENTING INDEPENDENT UPGRADER)
    db_dict = db.get_db_dict()
    db_dict['upgradeable'] = upgradeable

    db.overwrite_db(db_dict)

    if n_upgraded > 0:
        print(f'Upgrade successful. Upgraded packages: {n_upgraded}')
    else:
        print(f'Nothing to upgrade.')

def uninstall_(package, is_url, command=None):
    if is_url:
        url = package
    else:
        url = db.get_url_from_install_filename(package)

    # make sure package exists
    if url is None or not db.is_package_url(url):
        print('Package not found in database.')
        return

    # assume it exists from here on
    install_path = db.get_package_attribute(url, 'install_path')

    try:
        os.remove(install_path)
        print('Program removed...')
    except FileNotFoundError:
        print('Program not found in install path, skipping...')

    db.remove_package_entry(url)

    print('Package entry removed...')
    print('Package uninstalled.')

def list_(command=None):
    packages = db.get_db_dict()['packages']

    for url, package_metadata in packages.items():
        install_filename = package_metadata['install_filename']
        print(install_filename)

def init_(purge, command=None):
    if not init_getman.needs_init():
        answer = input('All getman files already exist. Run initialization'
                       ' anyways? (Will ask before overwriting files).'
                       ' (Y/n): ')

        if answer.lower in ['n', 'no']:
            print('Initialization cancelled. Nothing has been done.')
            return

    if purge:
        print('Requested purge. Directories that will be deleted before'
              ' running initialization:')
        print(DIR_PATH_DATA)
        print(DIR_PATH_CONFIG, '\n')

        answer = input('Type DELETE to proceed: ')

        if answer in ['DELETE']:
            init_getman.delete_everything()
            print('All getman directories deleted.\n')
        else:
            print('Exiting. Nothing has been deleted. Nothing has been done.')
            return

    init_getman.init_getman()

def _get_base64_md5(file_path):
    file_hash = hashlib.md5()

    with open(file_path, 'rb') as file:
        chunk = file.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = file.read(8192)

    b64_hash = b64encode(file_hash.digest()).decode()

    return b64_hash

def _get_headers(url):
    request = urllib.request.Request(url, method='HEAD')

    with urllib.request.urlopen(request) as response:
        return response.headers

if __name__ == '__main__':
    url = ('https://github.com/ThePBone/GalaxyBudsClient/releases/download'
           '/4.5.2/GalaxyBudsClient_Linux_64bit_Portable.bin')

    headers = _get_headers(url)

    download_filename = headers.get_filename() + '.test'

    download_filepath = os.path.join(DIR_PATH_PACKAGES, download_filename)
    urllib.request.urlretrieve(url, filename=download_filepath)

    print(f'download_filepath: {download_filepath}')

    print(f'headers:\n\n{headers}')
    print(f'content-md5 in headers:\n{headers["content-md5"]}\n')
    print(f'filename in headers:\n{headers.get_filename()}\n')

    if os.path.isfile(download_filepath):
        print(f'{download_filepath} successfully saved. Now removing.')
        os.remove(download_filepath)
    else:
        print(f'ERROR:\n{download_filepath} was not created.')
