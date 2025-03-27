import shutil
from datetime import datetime

import schedule
import time
import asyncio

from modules.database_api.interaction.insert import insert_logs
from modules.database_updater import downloader
from modules.database_updater import parser
from modules.database_updater import cleaner
from modules.images_updater import updater


def run_data_update():
    asyncio.run(downloader.run())
    parser.parse_all()
    cleaner.clean_all()
    updater.update()


def data_update_run_once():
    run_data_update()


def data_update_run_repeat():
    schedule.every(2).minutes.do(run_data_update)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    # data_update_run_once()
    data_update_run_repeat()
    # run_repeat()
