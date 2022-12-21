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
        DIR_PATH_DOWNLOADS,
        )

import database as db_module
import init_getman
import user_input

SUPPORTED_MIME_FIRSTS = ['application']
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
#       remove install on failed package entry?

def install_(url, pkg_name=None, force=False, command=None,
             update_only=False):
    db = db_module.DB()

    # DOWNLOAD FILE AND METADATA

    # headers is an EmailMessage => returns None if key not found
    headers = _get_headers(url)
    download_filename = headers.get_filename()
    mime_first = headers['content-type'].partition('/')[0]

    # TODO: Fetch the possible flags from argparser.
    #               Probably pass the entire parser
    if not force and db.is_package_url(url):
        pkg_name_old = db.get_package_attribute(url, 'name')
        print(f'Package already in database as {pkg_name_old}.'
               ' Use -f or --force to force install.')
        return

    if download_filename is None and pkg_name is None:
        print('Could not determine download filename.'
              ' Please provide custom name with --name')
        return

    if download_filename is None:
        download_filename = pkg_name
        print('NB: could not determine download_filename.'
              ' Using provided custom program name.')

    # Resolve different pkg_name when force-reinstalling package
    if db.is_package_url(url):
        pkg_name_old = db.get_package_attribute(url, 'name')

        if pkg_name != pkg_name_old:
            delete_old = user_input.prompt_yes_no(
                    f'Program previously installed as {pkg_name_old}'
                    f' (new name: {pkg_name}). Delete old program'
                     ' before re-installing with new name?',
                    default=True)

            if not delete_old:
                print('Keeping old install ({install_path_old})')
            else:
                install_path_old = os.path.join(DIR_PATH_INSTALL,
                                                pkg_name_old)

                try:
                    os.remove(install_path_old)
                    print(f'{install_path_old} deleted.')
                except FileNotFoundError:
                    print(f'{install_path_old} not found. Skipping deletion.')

    # a bit useless in its current state
    # TODO: proper warning
    if mime_first not in SUPPORTED_MIME_FIRSTS:
        print('Warning: could not determine if correct filetype before'
              ' downloading. Will check again after download.')

    download_path = os.path.join(DIR_PATH_DOWNLOADS, download_filename)

    # download file to download_path
    urllib.request.urlretrieve(url, filename=download_path)

    # INSTALL FILE

    if pkg_name is None:
        pkg_name = pathlib.Path(download_path).stem

    filetype = magic.from_file(download_path, mime=True)
    install_path = os.path.join(DIR_PATH_INSTALL, pkg_name)

    # Check for filename conflict (probably some redundant code somewhere)
    if os.path.isfile(install_path) and command != 'upgrade':
        url_other_package = db.get_url_from_pkg_name(pkg_name)

        if url_other_package == url:
            pass
        elif url_other_package is None:
            print(f'Unrecognized file with name "{pkg_name}" already'
                  f' exists in "{DIR_PATH_INSTALL}". Please install with'
                   ' alternate name using --name [NAME]. Aborting.')

            return
        else:
            print(f'"{pkg_name}" already exists in package database'
                  f' with url "{url_other_package}". Please install with'
                   ' alternate name using --name [NAME], or reinstall the'
                   ' other package with alternate name using'
                   ' --force --name [name]. Aborting.')

            return

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

    install_md5_base64 = _get_base64_md5(install_path)

    if command == 'upgrade':
        update_only = True

    package_entry_partial = {
            'url': url,
            'name': pkg_name,
            'install_path': install_path,
            'download_filename': download_filename,
            'md5_base64': install_md5_base64,
            'update_only': update_only}

    db.add_package_entry(**package_entry_partial)

    print(f'{pkg_name} successfully installed to {install_path}')

def update_(command=None):
    db = db_module.DB()

    packages = db.get_packages()

    for url, package_metadata in packages.items():
        headers = _get_headers(url)
        content_md5 = headers['content-md5']

        if content_md5 is None:
            print('Warning: not something isn\'t implemented yet'
                  ', skipping package Xd')
            continue

        if content_md5 != package_metadata['md5_base64']:
            db.add_upgradeable_entry(url)

    n_upgradeable = len(db.get_upgradeable())

    print(f'Update successful. Upgradeable packages: {n_upgradeable}')

def upgrade_(command=None):
    db = db_module.DB()

    upgradeable = db.get_upgradeable()
    n_upgraded = 0

    if len(upgradeable) == 0:
        print('Nothing to upgrade.')
        return

    # TODO: show total GB before upgrade (in install too)
    #       progress bar (in install too)
    #       probably make a separate upgrade uninstaller
    #       quote printed paths everywhere (this one isn't a path)
    #       more concrete exception? + better handling

    for url in upgradeable.keys():
        pkg_name = db.get_package_attribute(url, 'name')

        try:
            install_(url, pkg_name, force=True, update_only=True,
                     command=command)
        except Exception as e:
            print(f'Error during package installation. Package:'
                  f'{pkg_name} . Exception: {e}')
            continue

        db.remove_upgradeable_entry(url)
        n_upgraded += 1

    print( 'Upgrade completed. Upgraded packages:'
          f'{n_upgraded}/{len(upgradeable)}')

# TODO: rename package to pkg_name_or_url?
def uninstall_(package, is_url, command=None):
    db = db_module.DB()

    if is_url:
        url = package
    else:
        pkg_name = package
        url = db.get_url_from_pkg_name(pkg_name)

    if url is None or not db.is_package_url(url):
        print('Package not found in database.')
        return

    install_path = db.get_package_attribute(url, 'install_path')

    try:
        os.remove(install_path)
        print('Program removed...')
    except FileNotFoundError:
        print('Program not found in install path, skipping...')

    db.remove_package_entry(url=url)

    print('Package entry removed...')
    print('Package uninstalled.')

def list_(verbose=False, command=None):
    if verbose:
        _list_packages_verbose()
    else:
        _list_packages()

def _list_packages():
    db = db_module.DB()

    packages = db.get_packages()
    pkg_names = [db.get_package_attribute(url, 'name')
                 for url in packages.keys()]

    for pkg_name in pkg_names:
        print(pkg_name)

def _list_packages_verbose():
    db = db_module.DB()

    packages = db.get_packages()

    for url, package_metadata in packages.items():
        pkg_name = package_metadata['name']
        install_path = package_metadata['install_path']

        print(f'{pkg_name} \'{install_path}\''
              f'\n  {url}'
               '\n')

def init_(purge, command=None):
    db = db_module.DB()

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

        delete_binaries = user_input.prompt_yes_no(
                'Delete all installed binaries before purge?'
                ' (CANNOT BE DONE AUTOMATICALLY AFTER PURGE)',
                default=True)

        if delete_binaries:
            packages = db.get_packages()
            install_paths = [db.get_package_attribute(url, 'install_path')
                             for url in packages.keys()]

            for install_path in install_paths:
                try:
                    os.remove(install_path)
                    print(f'{install_path} removed')
                except FileNotFoundError:
                    print(f'{install_path} not found, skipping...')

            print('Found binaries deleted.')

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

