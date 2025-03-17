from src.config import config
import aiofiles
import aiohttp
from src.core.interfaces import ScheduleDownloaderInterface
from src.telegram_bot.utils.utils import configure_logging

configure_logging()
import logging

logger = logging.getLogger(__name__)


class ScheduleDownloader(ScheduleDownloaderInterface):

    async def download_schedule(self, file_url: str | None, study_type: str) -> str | None:
        if file_url is None:
            return None
        try:
            logger.info(f'Начало скачивания расписания для {study_type} групп')
            schedule_data = await self._download_schedule_file(file_url=file_url)

            if schedule_data is None:
                return None

            file_extension = await self._generate_extension_for_file(file_url=file_url)

            save_path = await self._create_save_path(study_type=study_type, extension=file_extension)

            await self._save_file(data=schedule_data, save_path=save_path)
            return save_path
        except Exception as e:
            raise Exception(f'Произошла ошибка при скачивании расписания {e}')

    @staticmethod
    async def _download_schedule_file(file_url: str) -> bytes | None:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    if response.status != 200:
                        return None
                    else:
                        return await response.read()
        except Exception as e:
            logger.error(f'Ошибка при скачивании расписания по ссылке {file_url}, {e}')
            raise Exception(f'Ошибка при скачивании расписания по ссылке {file_url}, {e}')

    @staticmethod
    async def _generate_extension_for_file(file_url: str) -> str:
        return file_url.split('/')[-1].split('.')[-1]

    @staticmethod
    async def _create_save_path(study_type: str, extension: str) -> str:
        file_name = ''

        if study_type == 'full_time':
            file_name = 'schedule_full_time'
        elif study_type == 'part_time':
            file_name = 'schedule_part_time'

        save_path = f'{config.SCHEDULE_FILES_DIRECTORY}\\{file_name}.{extension}'
        return save_path

    @staticmethod
    async def _save_file(data: bytes, save_path: str) -> None:
        try:
            async with aiofiles.open(save_path, 'wb') as file:
                await file.write(data)
        except Exception as e:
            logger.error(f'Ошибка при сохранении файла расписания {save_path}')
            raise Exception(f'Ошибка при сохранении файла расписания {save_path}')
