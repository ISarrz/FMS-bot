import shutil
from datetime import datetime

import schedule
import time
import asyncio

from modules.database_api.interaction.insert import insert_logs
from modules.database_updater.downloader import Web
from modules.database_updater import parser
from modules.database_updater import cleaner
from modules.images_updater import updater


class DataUpdater:
    def __init__(self, web):
        self.web = web

    async def run(self):
        await self.web.download_timetable()
        parser.parse_all()
        cleaner.clean_all()
        updater.update()

    @classmethod
    async def create(cls):
        web = await Web.create()
        return DataUpdater(web)


async def data_update_run_once():
    data_updater = await DataUpdater.create()
    await data_updater.run()


async def data_update_run_repeat():
    delay = 2 * 60 * 100
    data_updater = await DataUpdater.create()

    while True:
        await data_updater.run()
        time.sleep(delay)


if __name__ == "__main__":
    # data_update_run_once()
    asyncio.run(data_update_run_repeat())

    # run_repeat()
