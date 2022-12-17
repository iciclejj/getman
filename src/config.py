import json
import os

from constants import (
        FILE_PATH_CONFIG,
        FILE_PATH_DB,
        )

def init_config():
    config_dict = {
    }

    config_json = json.dumps(config_dict)

    with open(FILE_PATH_CONFIG, 'w+') as file:
        file.write(config_json)

    return FILE_PATH_CONFIG

def get_config():
    with open(FILE_PATH_CONFIG) as config_file:
        config_dict = json.loads(config_file.read())

    return config_dict

if __name__ == '__main__':
    if os.path.isfile(FILE_PATH_CONFIG):
        print(f'{FILE_PATH_CONFIG} already exists.\n')
        config_dict = get_config()
    else:
        print(f'{FILE_PATH_CONFIG} does not exist. Running init_config then deleting file.\n')
        config_path = init_config(FILE_PATH_DB)
        config_dict = get_config()
        os.remove(config_path)

    print(f'config json as dict:\n{config_dict}')
