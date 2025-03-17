import logging
from bs4 import BeautifulSoup
from src.core.interfaces import LinkParserInterface
from src.config import config
import aiohttp
from src.telegram_bot.utils.utils import configure_logging

configure_logging()

logger = logging.getLogger(__name__)

logging.info('Hi')
class LinkParser(LinkParserInterface):
    async def parse_links(self, url: str) -> dict | None:

        response = await self._get_page_with_links(url=url)
        if response is None:
            return None

        links_for_schedule = await self._parse_page_for_schedule_links(response_payload=response)
        if links_for_schedule is None:
            return None

        links_for_schedule_files = await self._create_links_for_schedule(links_for_schedule)
        logger.info('Ссылки на скачивание расписания получены')

        return links_for_schedule_files

    @staticmethod
    async def _get_page_with_links(url: str) -> bytes | None:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        logging.error(
                            msg=f'Ошибка во время получения ссылок для скачивания расписания - {response.status}')
                        return None
        except Exception as e:
            logging.error(msg=f'Ошибка во время получения ссылок для скачивания расписания - {e}')
            return None

    @staticmethod
    async def _parse_page_for_schedule_links(response_payload) -> dict | None:
        links = None
        try:
            soup = BeautifulSoup(response_payload, 'html.parser')
            links_for_schedule = soup.findAll(name='a', attrs={'class': 'mr-1 sf-link sf-link-theme sf-link-dashed'})

            if len(links_for_schedule) >= 2:
                links = dict()
                links['full_time'] = links_for_schedule[0]['href']
                links['part_time'] = links_for_schedule[1]['href']

            return links

        except Exception as e:
            logging.error(msg=f'Произошла ошибка во время парсинга ссылок со страницы - {e}')
            return None

    @staticmethod
    async def _create_links_for_schedule(raw_links: dict) -> dict:
        links = {}
        try:
            links['full_time'] = config.SITE_URL + raw_links['full_time']
            links['part_time'] = config.SITE_URL + raw_links['part_time']
            return links
        except Exception as e:
            logger.error(f'Ошибка при создании ссылок на загрузку расписания {e}')
