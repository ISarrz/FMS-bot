from modules.files_api.paths import config_path
import json


def get_config():
    with open(config_path) as f:
        response = json.load(f)

    return response


def get_config_fields(field):
    return get_config()[field]
