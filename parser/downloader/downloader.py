import urllib.request
import requests
from bs4 import BeautifulSoup
import lxml
import os
import asyncio


class Downloader:
    SCHEDULE_URL = "https://galaxycollege.ru/students/schedule/"

    def __init__(self, base_file_dir="files") -> None:
        current_path = os.path.dirname(os.path.abspath(__file__))
        self._current_path = os.path.join(current_path, base_file_dir)

    def _get_response(self):
        r = requests.get(self.SCHEDULE_URL)
        return r

    def _parse_links(self) -> tuple:
        r = self._get_response()
        soup = BeautifulSoup(r.text, 'html.parser')
        link1 = soup.findAll(name="a", attrs={"class": "mr-1 sf-link sf-link-theme sf-link-dashed"})[0]
        link2 = soup.findAll(name="a", attrs={"class": "mr-1 sf-link sf-link-theme sf-link-dashed"})[1]
        return link1, link2

    def _get_links(self) -> None:
        link1, link2 = self._parse_links()

        self.file_link1 = "https://galaxycollege.ru" + link1["href"]
        self.file_link2 = "https://galaxycollege.ru" + link2["href"]

    def _get_file(self, file_link, file_name) -> None:
        file = requests.get(file_link)
        with open(os.path.join(self._current_path, file_name), 'wb') as f:
            f.write(file.content)

    def _get_files(self) -> None:
        self._get_file(file_link=self.file_link1, file_name="schedule.xls")
        self._get_file(file_link=self.file_link2, file_name="schedule_zaoch.xls")

    def download_schedule(self) -> None:
        self._get_links()
        self._get_files()
