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

    def _get_links(self):
        r = requests.get(self.SCHEDULE_URL)
        soup = BeautifulSoup(r.text, 'html.parser')
        link1 = soup.findAll(name="a", attrs={"class": "mr-1 sf-link sf-link-theme sf-link-dashed"})[0]
        link2 = soup.findAll(name="a", attrs={"class": "mr-1 sf-link sf-link-theme sf-link-dashed"})[1]

        self.file_link1 = "https://galaxycollege.ru" + link1["href"]
        self.file_link2 = "https://galaxycollege.ru" + link2["href"]

    def _get_files(self) -> None:
        file1 = requests.get(self.file_link1)
        with open(os.path.join(self._current_path, "schedule.xls"), 'wb') as f:
            f.write(file1.content)
        file2 = requests.get(self.file_link2)
        with open(os.path.join(self._current_path, "schedule_zaoch.xls"), 'wb') as f:
            f.write(file2.content)

    def get_schedule(self) -> None:
        self._get_links()
        self._get_files()
