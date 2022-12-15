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

def get_config():
    with open(names.CONFIG_FILE_PATH) as config_file:
        config_dict = json.loads(config_file.read())
    return config_dict

if __name__ == '__main__':
    if os.path.isfile(names.CONFIG_FILE_PATH):
        print(f'{names.CONFIG_FILE_PATH} already exists.\n')
        config_dict = get_config()
    else:
        print(f'{names.CONFIG_FILE_PATH} does not exist. Running init_config then deleting file.\n')
        config_path = init_config(names.DEFAULT_DB_FILE_PATH)
        config_dict = get_config()
        os.remove(config_path)

    print(f'config json as dict:\n{config_dict}')
