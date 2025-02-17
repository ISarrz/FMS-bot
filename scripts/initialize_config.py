import json
from modules.files_api.paths import config_path
import modules.database_api


def initialize_config():
    config = {
        "telegram_api_token": input("Enter Telegram API token: "),
        "site_address": input("Enter site address: "),
        "site_login": input("Enter site login: "),
        "site_password": input("Enter site password: "),
        "admin_chat_id": int(input("Enter admin chat_id: "))
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)


if __name__ == "__main__":
    initialize_config()
