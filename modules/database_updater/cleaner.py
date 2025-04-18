from modules.time.dates import get_current_week, get_next_week, get_current_string_dates
from modules.files_api import downloads_path, parsed_files_path
from modules.database_api import *
import os
from modules.logger.logger import logger, async_logger


@logger
def clean_all():
    clean_files()
    clean_database()


def clean_files():
    downloaded_dates = [date.replace(".xlsx", "") for date in os.listdir(downloads_path)]
    parsed_dates = [date.replace(".xlsx", "") for date in os.listdir(parsed_files_path)]
    dates_pool = get_current_week() + get_next_week()
    string_dates_pool = [date.strftime('%d.%m') for date in dates_pool]

    for date in downloaded_dates:
        if date not in string_dates_pool:
            os.remove(os.path.join(downloads_path, date + ".xlsx"))

    for date in parsed_dates:
        if date not in string_dates_pool:
            os.remove(os.path.join(parsed_files_path, date + ".xlsx"))


def clean_database():
    clean_events()
    clean_images()
    clean_users_updates()


def clean_events():
    current_dates = get_current_string_dates()
    events = fetch_all_events()
    for event in events:
        if event['date'] not in current_dates:
            delete_event_by_id(event['id'])
            delete_group_event_by_event_id(event['id'])


def clean_images():
    current_dates = get_current_string_dates()
    images = fetch_all_images()
    for image in images:
        if image['date'] not in current_dates:
            delete_image_by_id(image['id'])


def clean_users_updates():
    current_dates = get_current_string_dates()
    users_updates = fetch_all_users_updates()
    for user_update in users_updates:
        if user_update['date'] not in current_dates:
            delete_users_updates_by_id(user_update['id'])


if __name__ == "__main__":
    clean_database()
    clean_files()
