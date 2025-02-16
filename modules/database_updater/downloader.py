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


# playwright install firefox
async def run(hide=True):
    async with async_playwright() as playwright:
        site_address = get_config_field('site_address')
        user_login = get_config_field('site_login')
        user_password = get_config_field('site_password')

        browser = await playwright.firefox.launch(headless=hide)
        page = await browser.new_page()

        await login(page, site_address, user_login, user_password)
        await go_to_news(page)
        await expand_news(page)
        await expand_news(page)
        current_news = await get_current_news(page)
        await download_files(page, current_news)
        await browser.close()


async def login(page, site_address, user_login, user_password):
    await page.goto(site_address)

    login_field = page.locator('input[autocomplete="username"]')
    password_field = page.locator('input[type="password"]')
    sing_in_button = page.locator("button.button--red")

    await login_field.fill(user_login)
    await password_field.fill(user_password)
    await sing_in_button.click()


async def go_to_news(page):
    news_button = page.locator('i[class="fal fa-fw fa-bullhorn"]')
    await news_button.click()


async def expand_news(page):
    news = page.locator('div.board-item')
    await expect(news).not_to_have_count(0)
    number = await news.count()
    for index in range(number - 1, -1, -1):
        cur = news.nth(index)
        news_is_active = await cur.locator('div.board-item__content').is_visible()
        if not news_is_active:
            roll_down = cur.locator('div.board-item__title')
            await roll_down.click()


async def get_current_news(page):
    dates_pool = get_current_week() + get_next_week()
    downloaded_dates = [date.replace(".xlsx", "") for date in os.listdir(downloads_path)]
    downloaded_dates += [date.replace(".xlsx", "") for date in os.listdir(parsed_files_path)]
    string_dates_pool = [date.strftime('%d.%m') for date in dates_pool if
                         date.strftime('%d.%m') not in downloaded_dates]

    current_news = []
    news = page.locator('div.board-item')
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


async def download_files(page, dates):
    for date in dates:
        async with page.expect_download() as download_info:
            button = date.locator('a.button--purple').first
            await button.click()
            download = await download_info.value

        await download.save_as(os.path.join(downloads_path, download.suggested_filename))


async def main():
    await run(hide=True)


if __name__ == '__main__':
    asyncio.run(main())
