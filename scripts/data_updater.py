import schedule
import time
import asyncio

from modules.data_updater.web_parser.web_parser import WebParser
from modules.data_updater.data_cleaner.data_cleaner import DataCleaner
from modules.data_updater.files_parser.parser import Parser
from modules.data_updater.painter import updater
from modules.logger.logger import logger


def run_painter():
    updater.update()


def run_parser():
    Parser().parse_all()


def run_data_cleaner():
    DataCleaner().clean_all()


async def web_parse():
    parser = WebParser()
    await parser.download()
    await parser.close()


def run_web_parser():
    asyncio.run(web_parse())


@logger
def run_data_update():
    run_data_cleaner()
    run_web_parser()
    run_parser()
    run_painter()


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
