import asyncio
from playwright.async_api import async_playwright, Page, expect
from modules.time.dates import get_current_week, get_next_week
from modules.files_api import (
    get_config,
    get_config_field
)
from modules.files_api import downloads_path, parsed_files_path
import shutil
import os
from modules.logger.logger import async_logger, logger


class Web:
    def __init__(self, browser, page):
        self.browser = browser
        self.page = page

    @classmethod
    async def create(cls, hide=True):
        browser, page = await cls.async_init(hide)
        web = Web(browser, page)
        await web.login()
        return web

    @staticmethod
    async def async_init(hide):
        playwright_t = await async_playwright().start()

        browser = await playwright_t.firefox.launch(headless=hide)

        page = await browser.new_page()
        return browser, page

    async def login(self):
        await self.page.goto(get_config_field('site_address'))

        login_field = self.page.locator('input[autocomplete="username"]')
        password_field = self.page.locator('input[type="password"]')
        sing_in_button = self.page.locator("button.button--red")

        await login_field.fill(get_config_field('site_login'))
        await password_field.fill(get_config_field('site_password'))
        await sing_in_button.click()


    async def download_timetable(self):
        await self.go_to_news()
        await self.expand_news()
        await self.expand_news()
        current_news = await self.get_current_news()
        await self.download_files(current_news)

    async def go_to_news(self):
        news_button = self.page.locator('i[class="fal fa-fw fa-bullhorn"]')
        await news_button.click()

    async def expand_news(self):
        news = self.page.locator('div.board-item')
        await expect(news).not_to_have_count(0)
        number = await news.count()
        for index in range(number - 1, -1, -1):
            cur = news.nth(index)
            news_is_active = await cur.locator('div.board-item__content').is_visible()
            if not news_is_active:
                roll_down = cur.locator('div.board-item__title')
                await roll_down.click()

    async def get_current_news(self):
        dates_pool = get_current_week() + get_next_week()
        downloaded_dates = [date.replace(".xlsx", "") for date in os.listdir(downloads_path)]
        downloaded_dates += [date.replace(".xlsx", "") for date in os.listdir(parsed_files_path)]
        string_dates_pool = [date.strftime('%d.%m') for date in dates_pool if
                             date.strftime('%d.%m') not in downloaded_dates]

        current_news = []
        news = self.page.locator('div.board-item')
        number = await news.count()
        for i in range(number):
            cur_news = news.nth(i)
            text = await cur_news.inner_text()
            text = text.lower()
            if "расписание" not in text or "урок" not in text:
                continue

            file = cur_news.locator('span[class="button__title"]')
            file_name = await file.inner_text()
            file_name = file_name.strip().replace('.xlsx', '')

            if file_name in string_dates_pool:
                current_news.append(cur_news)

        return current_news

    async def download_files(self, dates):
        for date in dates:
            async with self.page.expect_download() as download_info:
                button = date.locator('a.button--purple').first
                await button.click()
                download = await download_info.value

            await download.save_as(os.path.join(downloads_path, download.suggested_filename))

    async def close(self):
        self.browser.close()

    # playwright install firefox


async def main():
    web = await Web.create(hide=False)
    await web.download_timetable()
    await web.download_timetable()
    await web.close()
    pass


if __name__ == '__main__':
    asyncio.run(main())
