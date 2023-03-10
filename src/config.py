import json

from constants import (
        FILE_PATH_CONFIG,
        )

def init_config():
    config_dict = {
    }

    config_json = json.dumps(config_dict)

    with open(FILE_PATH_CONFIG, 'w+', encoding='utf-8') as config_file:
        config_file.write(config_json)

    return FILE_PATH_CONFIG

def get_config():
    with open(FILE_PATH_CONFIG, 'r', encoding='utf-8') as config_file:
        config_dict = json.loads(config_file.read())

    return config_dict

