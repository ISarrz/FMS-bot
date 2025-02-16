import json
from modules.files_api.paths import config_path


def initialize_config():
    config = {
        "telegram_api_key": input("Enter Telegram API key: "),
        "site_address": input("Enter site address: "),
        "site_login": input("Enter site login: "),
        "site_password": input("Enter site password: "),
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)


if __name__ == "__main__":
    initialize_config()
