import requests
import logging
from bs4 import BeautifulSoup
from requests import Response
from src.core.interfaces import LinkParserInterface
from src.config import SITE_URL

logger = logging.getLogger(__name__)


class LinkParser(LinkParserInterface):
    def parse_links(self, url: str) -> tuple[str, str]:

        response = self._get_links(url=url)

        links_for_schedule = self._parse_site_for_schedule_links(response=response)
        links_for_schedule_files = self._create_links_for_schedule(links_for_schedule)

        logger.info("Ссылки на скачивание расписания получены")

        return links_for_schedule_files

    @staticmethod
    def _get_links(url: str) -> Response:
        response = requests.get(url)
        if response.status_code != 200:
            logger.error(msg=f"Ошибка во время получения ссылок для скачивания расписания")
            raise Exception("Ошибка во время получения ссылок на скачивание расписания")
        else:
            return response

    @staticmethod
    def _parse_site_for_schedule_links(response) -> list:
        try:

            soup = BeautifulSoup(response.text, "html.parser")
            links_for_schedule = soup.findAll(name="a", attrs={"class": "mr-1 sf-link sf-link-theme sf-link-dashed"})

            link_for_full_time_schedule = links_for_schedule[0]["href"]
            link_for_part_time_schedule = links_for_schedule[1]["href"]

            return [link_for_full_time_schedule, link_for_part_time_schedule]

        except Exception as e:
            raise Exception("Ошибка при парсинге расписания")

    @staticmethod
    def _create_links_for_schedule(links: list) -> tuple[str, str]:
        link_for_full_time_schedule = SITE_URL + links[0]
        link_for_part_time_schedule = SITE_URL + links[1]
        return link_for_full_time_schedule, link_for_part_time_schedule
