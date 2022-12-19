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
import user_input

# TODO: create separate .py files for each command
#               and turn this into an "interface" file

# must match SUPPORTED_CONTENT_TYPE_FIRSTS with startswith
#         (text after '/' is excluded from this list)
SUPPORTED_CONTENT_TYPE_FIRSTS = ['application']
SUPPORTED_FILETYPES = ['application/x-pie-executable']

# fix [SSL: CERTIFICATE_VERIFY_FAILED] error on some devices
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
ssl._create_default_https_context = lambda: SSL_CONTEXT

# TODO: CHECK IF FILE ALREADY EXISTS IN bin DIR. confirm whether you're
#               confirm whether you're overwriting correct one using md5
#
#       EXPERIMENTAL TODOS:
#       auto-detect system/architecture
#       auto-detect site-specific preferred download urls
#               (for example from git repo)
#       use api when supported (for example api.github.com)
def install_(url, install_filename=None, force=False, command=None):
    db_dict = db.get_db_dict()

    # DOWNLOAD FILE AND METADATA

    # headers is an EmailMessage => returns None if key not found
    headers = _get_headers(url)
    download_filename = headers.get_filename()
    content_type_first = headers['content-type'].partition('/')[0]

    # TODO: Fetch the possible flags from argparser.
    #               Probably pass the entire parser
    if download_filename is None:
        if install_filename is None:
            print('Could not determine download filename.'
                  ' Please provide custom name with --name')
            return

        download_filename = install_filename
        print('NB: could not determine download_filename.'
              ' Using provided custom program name.')

    if not force and url in db_dict['packages']:
        install_filename_curr = db_dict['packages'][url]['install_filename']
        print(f'Package already in database as {install_filename_curr}.'
               ' Use -f or --force to force install.')
        return

    # Resolve different install_filename when force-reinstalling package
    if url in db_dict['packages']:
        install_filename_old = db_dict['packages'][url]['install_filename']

        if install_filename != install_filename_old:
            delete_old = user_input.prompt_yes_no(
                    f'Program previously installed as {install_filename_old}'
                    f' (new name: {install_filename}). Delete old program'
                     ' before re-installing with new name?',
                    default=True)

            if not delete_old:
                print('Keeping old install ({install_path_old})')
            else:
                install_path_old = os.path.join(DIR_PATH_INSTALL,
                                                install_filename_old)

                try:
                    os.remove(install_path_old)
                    print(f'{install_path_old} deleted.')
                except FileNotFoundError:
                    print(f'{install_path_old} not found. Skipping deletion.')

    # a bit useless in its current state
    # TODO: proper warning
    if content_type_first not in SUPPORTED_CONTENT_TYPE_FIRSTS:
        print('Warning: could not determine if correct filetype before'
              ' downloading. Will check again after download.')

    download_path = os.path.join(DIR_PATH_PACKAGES, download_filename)

    # download file to download_path
    urllib.request.urlretrieve(url, filename=download_path)

    # INSTALL FILE

    if install_filename is None:
        install_filename = pathlib.Path(download_path).stem

    filetype = magic.from_file(download_path, mime=True)
    install_path = os.path.join(DIR_PATH_INSTALL, install_filename)

    # TODO probably don't delete the old install before checking this
    if filetype not in SUPPORTED_FILETYPES:
        os.remove(download_path)
        raise ValueError(f'Unsupported filetype: {filetype}')

    # TODO: make this less hard-coded
    #       handle replace error
    try:
        if filetype == 'application/x-pie-executable':
            file_st = os.stat(download_path)
            plus_x_mode = (file_st.st_mode | stat.S_IXUSR | stat.S_IXGRP
                           | stat.S_IXOTH)
            os.chmod(download_path, plus_x_mode)
            os.replace(download_path, install_path)
    except PermissionError as e:
        raise PermissionError('Run with sudo (\'sudo -E\' if running getman as'
                              'a python script)') from e

    install_md5 = _get_base64_md5(install_path)

    db_dict['packages'][url] = {
            'created_at': str(datetime.now()),
            'updated_at': str(datetime.now()),
            'install_filename': install_filename,
            'install_path': install_path,
            'download_filename': download_filename,
            'md5_base64': install_md5,
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
        install_(url, install_filename, force=True)
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
    # TODO: add option to delete all installed binaries before purging db
    if not init_getman.needs_init():
        force_init = user_input.prompt_yes_no(
                'All getman files already exist. Run initialization anyways?'
                ' (Will ask before overwriting files).',
                default=True)

        if not force_init:
            print('Initialization cancelled. Nothing has been done.')
            return

    if purge:
        confirm_purge = user_input.prompt_exact(
                'Requested purge. Directories that will be deleted before'
                f' running initialization:\n{DIR_PATH_DATA}\n{DIR_PATH_CONFIG}',
                true_inputs=['DELETE'])

        if not confirm_purge:
            print('Exiting. Nothing has been deleted. Nothing has been done.')
            return

        init_getman.delete_everything()
        print('All getman directories deleted.')

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
