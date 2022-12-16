# python standard libraries
import hashlib
import json
import os
import subprocess
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
import filenames as names
import database as db
import config
import init_getman

# TODO: create separate .py files for each command and turn this into an "interface" file

SUPPORTED_CONTENT_TYPE_FIRSTS = ['application'] # must use startswith (after '/' is excluded)
SUPPORTED_FILETYPES = ['application/x-pie-executable']

# fix [SSL: CERTIFICATE_VERIFY_FAILED] error on some devices
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
ssl._create_default_https_context = lambda: SSL_CONTEXT

# TODO: 
#
#       EXPERIMENTAL TODOS:
#       auto-detect system/architecture
#       auto-detect site-specific preferred download urls (for example from git repo)
#       use api when supported (for example api.github.com)
def install_(url, install_filename=None, force=False, db_name=None,
             command=None):
    db_dict = db.get_db_dict(db_name)
    
    # download file and metadata
    headers = _get_headers(url) # headers is an EmailMessage => returns None if key not found

    download_filename = headers.get_filename()
    content_type_first = headers['content-type'].partition('/')[0]

    # TODO: maybe turn return into exception
    if download_filename is None:
        if install_filename is None:
            print('Could not determine download filename.'
                  ' Please provide custom name with --name')
            return

        download_filename = install_filename
        print('NB: could not determine download_filename.'
              ' Using provided custom program name.')

    # TODO: make listing of filename nicer (currently shows download_filename)
    #       resolve new install_filename for same url when force == True
    if not force and url in db_dict['packages']:
        install_filename_curr = db_dict['packages'][url]['install_filename']
        print(f'Package already in database as {install_filename_curr}')
        return

    # a bit useless in its current state
    if content_type_first not in SUPPORTED_CONTENT_TYPE_FIRSTS:
        print('Warning: could not determine if correct filetype before downloading.'
              ' Will check again after download.') # TODO: proper warning

    download_path = os.path.join(names.DEFAULT_DEB_PACKAGE_DIR_PATH, download_filename)
    urllib.request.urlretrieve(url, filename=download_path) # downloads file to download_path

    # install file
    filetype = magic.from_file(download_path, mime=True)

    if install_filename is None:
        install_filename = pathlib.Path(download_path).stem

    install_path = os.path.join(names.INSTALL_DIR_PATH, install_filename)

    # TODO: maybe make a general error handler for the install command
    if filetype not in SUPPORTED_FILETYPES:
        os.remove(download_path)
        raise ValueError(f'Unsupported filetype: {filetype}')

    # TODO: make this less hard-coded
    try:
        if filetype == 'application/x-pie-executable':
            file_st = os.stat(download_path)
            os.chmod(download_path, file_st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            os.replace(download_path, install_path)
    except Exception  as e: # TODO: HANDLE THIS PROPERLY !!!
        os.remove(download_path)
        print(e)
        print('Run with sudo (\'sudo -E\' if running getman as a python script)')
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

    db.overwrite_db(db_name, db_dict)

    print(f'{install_filename} successfully installed to {install_path}')

def update_(db_name=None, command=None):
    db_dict = db.get_db_dict(db_name)

    for url, package_metadata in db_dict['packages'].items():
        headers = _get_headers(url)
        content_md5 = headers['content-md5'] # TODO: maybe rename content_md5 to md5_base64 (everywhere)

        if content_md5 is None:
            print('Warning: not something isn\'t implemented yet, skipping package Xd')
            continue

        if content_md5 != package_metadata['md5_base64']:
            db_dict['upgradeable'][url] = {}

    db.overwrite_db(db_name, db_dict)

    upgradeable = db.get_db_dict(db_name)['upgradeable']
    n_upgradeable = len(upgradeable)

    print(f'Update successful. Upgradeable packages: {n_upgradeable}')

def upgrade_(db_name=None, command=None):
    upgradeable = db.get_db_dict(db_name)['upgradeable']

    n_upgraded = 0

    # TODO: try/except
    #       show total GB before upgrade (in install too)
    #       progress bar (in install too)
    for url in list(upgradeable.keys()): # list to allow delete as we go
        install_filename = db.get_package_attribute(db_name, url,
                                                    'install_filename')
        install(url, install_filename, force=True) # TODO: probably make a separate upgrade installer
        del upgradeable[url]
        n_upgraded += 1

    # reload db_dict after modification by install (REMOVE IF IMPLEMENTING INDEPENDENT UPGRADER)
    db_dict = db.get_db_dict(db_name)
    db_dict['upgradeable'] = upgradeable

    db.overwrite_db(db_name, db_dict)

    if n_upgraded > 0:
        print(f'Upgrade successful. Upgraded packages: {n_upgraded}')
    else:
        print(f'Nothing to upgrade.')

def uninstall_(package, is_url, db_name=None, command=None):
    if is_url:
        url = package
    else:
        url = db.get_url_from_install_filename(db_name, package)

    # make sure package exists
    if url is None or not db.is_package_url(db_name, url):
        print('Package not found in database.')
        return

    # assume it exists from here on
    install_path = db.get_package_attribute(db_name, url, 'install_path')

    try:
        os.remove(install_path)
        print('Program removed...')
    except FileNotFoundError as e:
        print('Program not found in install path, skipping...')

    db.remove_package_entry(db_name, url)

    print('Package entry removed...')
    print('Package uninstalled.')

def list_(db_name=None, command=None):
    packages = db.get_db_dict(db_name)['packages']

    for url, package_metadata in packages.items():
        install_filename = package_metadata['install_filename']
        print(install_filename)

def init_(purge, command=None):
    if not init_getman.needs_init():
        answer = input('All getman files already exist. Run initialization'
                       ' anyways? (Will ask before overwriting files). (Y/n): ')

        if answer not in ['y', 'Y', '']:
            print('Initialization cancelled. Nothing has been done.')
            return

    if purge:
        print('Requested purge. Directories that will be deleted before running'
              ' initialization:')
        print(names.DATA_DIR_PATH)
        print(names.CONFIG_DIR_PATH, '\n')

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
    response = urllib.request.urlopen(request)

    return response.headers

if __name__ == '__main__':
    url = 'https://github.com/ThePBone/GalaxyBudsClient/releases/download/4.5.2/GalaxyBudsClient_Linux_64bit_Portable.bin'

    headers = _get_headers(url)

    download_filename = headers.get_filename() + '.test'

    download_filepath = os.path.join(names.DEFAULT_DEB_PACKAGE_DIR_PATH, download_filename)
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

