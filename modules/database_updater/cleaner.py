from modules.time.dates import get_current_week, get_next_week
from modules.files_api import downloads_path, parsed_files_path
from modules.database_api import (
    fetch_all_events,
    delete_event_by_id
)
import os


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


def clean_events():
    current_dates = get_current_week() + get_next_week()
    current_string_dates = [date.strftime('%d.%m') for date in current_dates]
    events = fetch_all_events()
    for event in events:
        if event.date not in current_string_dates:
            delete_event_by_id(event.id)
