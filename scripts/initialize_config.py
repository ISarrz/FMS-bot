import json
from modules.config.paths import config_path


def initialize_config():
    config = {
        "telegram_api_token": input("Enter Telegram API token: "),
        "site_address": input("Enter site address: "),
        "site_login": input("Enter site login: "),
        "site_password": input("Enter site password: "),
        "admin_chat_id": int(input("Enter admin chat_id: ")),
        "logs_chat_id": int(input("Enter logs_chat_id: ")),
        "yandex_key": input("Enter yandex_key: "),
        "yandex_secret_key": input("Enter yandex_secret_key: "),
        "yandex_bucket_address": input("Enter yandex_bucket_address: "),
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)


if __name__ == "__main__":
    initialize_config()
