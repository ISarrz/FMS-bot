from modules.time.dates import get_current_string_dates
from modules.config.paths import downloaded_files_path, parsed_files_path
from modules.database import *
import os


# from modules.logger.logger import logger, async_logger

class DataCleaner:
    def clean_all(self):
        self.clean_files()
        self.clean_database()

    @staticmethod
    def clean_files():
        downloaded_dates = [date.replace(".xlsx", "") for date in os.listdir(downloaded_files_path)]
        parsed_dates = [date.replace(".xlsx", "") for date in os.listdir(parsed_files_path)]
        dates_pool = get_current_string_dates()

        for date in downloaded_dates:
            if date not in dates_pool:
                os.remove(os.path.join(downloaded_files_path, date + ".xlsx"))

        for date in parsed_dates:
            if date not in dates_pool:
                os.remove(os.path.join(parsed_files_path, date + ".xlsx"))

    def clean_database(self):
        self.clean_events()
        self.clean_timetable()

    @staticmethod
    def clean_events():
        current_dates = get_current_string_dates()
        events = Event.all()
        for event in Event.all():
            if event.date not in current_dates:
                event.delete()

    @staticmethod
    def clean_timetable():
        current_dates = get_current_string_dates()
        for timetable in Timetable.all():
            if timetable.date not in current_dates:
                timetable.delete()


if __name__ == "__main__":
    DataCleaner().clean_all()
