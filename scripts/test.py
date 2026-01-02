import subprocess
from modules.config.paths import database_path
from modules.config.config import get_config_field
from datetime import datetime
import xml.etree.ElementTree as ET





def load_backup(backup_name: str):
    cmd = ["curl",
           "--request", "GET",
           "--user", f"{get_config_field("yandex_key")}:{get_config_field("yandex_secret_key")}",
           "--aws-sigv4", "aws:amz:ru-central1:s3",
           "--verbose",
           f"{get_config_field("yandex_bucket_address")}/{backup_name}"
           ]

    with open(database_path, "wb") as f:
        result = subprocess.run(
            cmd,
            stderr=subprocess.PIPE,
            stdout=f
        )

    return result.returncode


def get_backups_names():
    cmd = ["curl",
           "--request", "GET",
           "--user", f"{get_config_field("yandex_key")}:{get_config_field("yandex_secret_key")}",
           "--aws-sigv4", "aws:amz:ru-central1:s3",
           "--verbose",
           f"{get_config_field("yandex_bucket_address")}?list-type=2"
           ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )

    xml_data = result.stdout
    root = ET.fromstring(xml_data)
    ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
    files = [
        elem.text
        for elem in root.findall(".//s3:Contents/s3:Key", ns)
    ]

    return files


def load_last_backup():
    backups_names = get_backups_names()
    backups_names.sort(key=lambda s: datetime.strptime(s, "%d-%m-%Y"))

    return load_backup(backups_names[-1])


if __name__ == "__main__":
    get_backups_names()
