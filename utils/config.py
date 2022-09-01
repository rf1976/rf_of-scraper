r"""
               _          __                                                                      
  ___   _ __  | | _   _  / _|  __ _  _ __   ___         ___   ___  _ __   __ _  _ __    ___  _ __ 
 / _ \ | '_ \ | || | | || |_  / _` || '_ \ / __| _____ / __| / __|| '__| / _` || '_ \  / _ \| '__|
| (_) || | | || || |_| ||  _|| (_| || | | |\__ \|_____|\__ \| (__ | |   | (_| || |_) ||  __/| |   
 \___/ |_| |_||_| \__, ||_|   \__,_||_| |_||___/       |___/ \___||_|    \__,_|| .__/  \___||_|   
                  |___/                                                        |_|                
"""

import json
import pathlib

from .prompts import config_prompt
from ..constants import configPath, configFile, mainProfile


def read_config():
    p = pathlib.Path.home() / configPath
    if not p.is_dir():
        p.mkdir(parents=True, exist_ok=True)

    while True:
        try:
            with open(p / configFile, 'r') as f:
                config = json.load(f)

            try:
                if [*config['config']] != [*get_current_config_schema(config)['config']]:
                    config = auto_update_config(p, config)
            except KeyError:
                raise FileNotFoundError

            break
        except FileNotFoundError:
            file_not_found_message = f"You don't seem to have a `config.json` file. One has been automatically created for you at: '{p / configFile}'"

            make_config(p)
            print(file_not_found_message)
    return config


def get_current_config_schema(config: dict) -> dict:
    config = {
        'config': {
            mainProfile: config['config'][mainProfile] or mainProfile,
        }
    }
    return config


def make_config(path):
    config = {
        'config': {
            mainProfile: mainProfile,
        }
    }

    with open(path / configFile, 'w') as f:
        f.write(json.dumps(config, indent=4))


def update_config(field: str, value):
    p = pathlib.Path.home() / configPath / configFile

    with open(p, 'r') as f:
        config = json.load(f)

    config['config'].update({field: value})

    with open(p, 'w') as f:
        f.write(json.dumps(config, indent=4))


def auto_update_config(path, config: dict) -> dict:
    new_config = get_current_config_schema(config)

    with open(path / configFile, 'w') as f:
        f.write(json.dumps(new_config, indent=4))

    return new_config


def edit_config():
    p = pathlib.Path.home() / configPath / configFile

    with open(p, 'r') as f:
        config = json.load(f)

    updated_config = config_prompt(config['config'])

    with open(p, 'w') as f:
        f.write(json.dumps(updated_config, indent=4))

    print('`config.json` successfully edited.')
