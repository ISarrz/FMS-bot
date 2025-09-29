import os
import re
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup
import httpx

from modules.config.paths import downloaded_files_path, parsed_files_path
from modules.config.config import get_config_field
from modules.time import get_current_string_dates, get_current_week_string_days
from modules.statistics.statistics import get_statistics_field, set_statistics_field


class WebParser:
    base_url = "https://fms.eljur.ru"
    site_login = get_config_field("site_login")
    site_password = get_config_field("site_password")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115 Safari/537.36"
    }

    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers
        )

    @staticmethod
    def get_pool_files():
        downloaded_files = os.listdir(downloaded_files_path) + os.listdir(parsed_files_path)
        dates_pool = get_current_string_dates()

        pool_files = [date + ".xlsx" for date in dates_pool if date + ".xlsx" not in downloaded_files]
        return pool_files

    async def download(self):
        success = await self.login()

        if not success:
            print("Login failed")
            return

        items = await self.parse_board()
        for item in items:
            await self.parse_item(item)

    async def login(self) -> bool:
        login_url = "/ajaxauthorize"
        data = {
            "username": self.site_login,
            "password": self.site_password,
            "return_uri": "/"
        }
        response = await self.client.post(login_url, data=data)
        result = response.json()

        return result.get("result") and result.get("actions")[0].get("type") == "redirect"

    async def parse_board(self):
        board_url = "/journal-board-action"
        response = await self.client.get(board_url)
        soup = BeautifulSoup(response.text, "lxml")

        return soup.find_all(class_="board-item")

    async def parse_item(self, item):
        title = item.find(class_="board-item__title").text.strip().lower()
        if "спец" in title or "клуб" in title or "расписание" not in title:
            return

        button = item.find("a", class_="button button--outline button--purple")
        if not button:
            return

        button_title = button.find(class_="button__title")
        if not button_title:
            return

        title_text = button_title.text.strip()

        match = re.search(r"\b\d{2}\.\d{2}\b", title_text)
        if not match:
            return

        current_year = datetime.now().year
        filename = match.group() + f".{current_year}.xlsx"

        # if filename not in WebParser.get_pool_files():
        #     return

        file_url = button.attrs.get("href")
        if not file_url:
            return

        response = await self.client.get(file_url)
        file_path = os.path.join(downloaded_files_path, filename)

        with open(file_path, "wb") as f:
            f.write(response.content)

    async def close(self):
        await self.client.aclose()


if __name__ == "__main__":
    async def main():
        d = WebParser()
        await d.download()
        await d.close()  # освобождаем ресурсы


    asyncio.run(main())
