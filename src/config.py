import json
import os

import filenames as names

def init_config(db_path):
    config_path = names.CONFIG_FILE_PATH

    config_dict = {
            'db_path': db_path
    }

    config_json = json.dumps(config_dict)

    with open(config_path, 'w+') as file:
        file.write(config_json)

    return config_path
