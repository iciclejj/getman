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

# pip libraries
import magic

# local modules
import filenames as names
import database as db

# TODO: create separate .py files for each command and turn this into an "interface" file

SUPPORTED_CONTENT_TYPE_FIRSTS = ['application'] # must use startswith (after '/' is excluded)
SUPPORTED_FILETYPES = ['application/x-pie-executable']

def install(url, db_name=None):
    # load database
    if db_name is None:
        db_name = names.DEFAULT_DB_FILE_NAME

    db_path = os.path.join(names.DB_DIR_PATH, db_name)

    with open(db_path, 'r') as db_file:
        db_dict = json.loads(db_file.read())
    
    # download file and metadata
    headers = _get_headers(url) # headers is an EmailMessage => returns None if key not found

    download_filename = headers.get_filename()

    content_type_first = headers['content-type'].partition('/')[0]

    # TODO: make listing of filename nicer (currently shows download_filename)
    if url in db_dict['packages']:
        print(f'{download_filename} already in database')
        return

    # a bit useless in its current state
    if content_type_first not in SUPPORTED_CONTENT_TYPE_FIRSTS:
        print('Warning: could not determine if correct filetype before downloading') # TODO: proper warning

    download_path = os.path.join(names.DEFAULT_DEB_PACKAGE_DIR_PATH, download_filename)
    urllib.request.urlretrieve(url, filename=download_path) # downloads file

    # install file
    filetype = magic.from_file(download_path, mime=True)
    filename_stem = pathlib.Path(download_path).stem

    install_path = os.path.join(names.INSTALL_DIR_PATH, filename_stem)

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
        print('Run with \'sudo -E\'')
        return

    content_md5 = _get_base64_md5(install_path)

    db_dict['packages'][url] = {
            'created_at': str(datetime.now()),
            'updated_at': str(datetime.now()),
            'install_filename': filename_stem,
            'install_path': install_path,
            'download_filename': download_filename,
            'md5_base64': content_md5,
    }

    db.overwrite_db(db_path, db_dict)

def update(db_name=None):
    if db_name is None:
        db_name = names.DEFAULT_DB_FILE_NAME

    db_path = os.path.join(names.DB_DIR_PATH, db_name)

    with open(db_path, 'r') as db_file:
        db_dict = json.loads(db_file.read())

    for url, metadata in db_dict['packages'].items():
        headers = _get_headers(url)
        content_md5 = headers['content-md5'] # TODO: maybe rename content_md5 to md5_base64 (everywhere)

        if content_md5 is None:
            print('Warning: not something isn\'t implemented yet, skipping package Xd')
            continue

        if content_md5 != metadata['md5_base64']:
            db_dict['upgradeable'][url] = {}

    db.overwrite_db(db_path, db_dict)

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

    filename = headers.get_filename()

    filepath = os.path.join(names.DEFAULT_DEB_PACKAGE_DIR_PATH, filename)
    local_filepath = urllib.request.urlretrieve(url, filename=filepath)

    print(local_filepath, '\n\n')

    print(headers)
    print(headers['content-md5'])
    print(headers.get_filename())
    

