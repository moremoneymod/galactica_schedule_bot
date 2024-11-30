import logging

import requests
from bs4 import BeautifulSoup

from src.core.interfaces import LinkParserInterface
import logging

logger = logging.getLogger(__name__)


class LinkParser(LinkParserInterface):
    @staticmethod
    def parse_link(url: str) -> tuple[str, str]:
        response = requests.get(url)

        if response.status_code != 200:
            logging.error(msg=f"Ошибка во время получения ссылок на скачивания расписания")
            raise Exception("Ошибка во время получения ссылок на скачивание расписания")

        soup = BeautifulSoup(response.text, "html.parser")
        link1 = soup.findAll(name="a", attrs={"class": "mr-1 sf-link sf-link-theme sf-link-dashed"})[0]
        link2 = soup.findAll(name="a", attrs={"class": "mr-1 sf-link sf-link-theme sf-link-dashed"})[1]

        file_link1 = "https://galaxycollege.ru" + link1["href"]
        file_link2 = "https://galaxycollege.ru" + link2["href"]

        logger.info("Ссылки на скачивание расписания получены")

        return file_link1, file_link2
