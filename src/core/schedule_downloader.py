import requests
import logging

from requests import Response

from src.core.interfaces import ScheduleDownloaderInterface

logger = logging.getLogger(__name__)


class ScheduleDownloader(ScheduleDownloaderInterface):
    def __init__(self, directory_manager):
        self.directory_manager = directory_manager

    def download_schedule(self, file_url: str, study_type: str):
        schedule_data = self._download_schedule_file(file_url=file_url)

        extension = self._generate_extension_for_file(file_url=file_url)

        save_path = self._create_save_path(study_type=study_type, extension=extension)

        self._save_file(data=schedule_data, save_path=save_path)

        logger.info(f"Успешно сохранено расписание по пути {save_path}")

        return save_path

    @staticmethod
    def _download_schedule_file(file_url: str) -> bytes:
        response = requests.get(file_url)
        if response.status_code != 200:
            logger.error(f"Ошибка при скачивании расписания по ссылке {file_url}")
            raise Exception(f"Ошибка при скачивании расписания по ссылке {file_url}")
        else:
            return response.content

    @staticmethod
    def _generate_extension_for_file(file_url: str) -> str:
        return file_url.split('/')[-1].split('.')[-1]

    def _create_save_path(self, study_type: str, extension: str) -> str:
        file_name = ""

        if study_type == "full_time":
            file_name = "schedule_full_time"
        elif study_type == "part_time":
            file_name = "schedule_part_time"

        save_path = f"{self.directory_manager.get_download_directory()}/{file_name}.{extension}"
        return save_path

    @staticmethod
    def _save_file(data: bytes, save_path: str) -> None:
        try:
            with open(save_path, "wb") as file:
                file.write(data)
        except Exception as e:
            logger.error(f"Ошибка при сохранении файла расписания {save_path}")
            raise Exception(f"Ошибка при сохранении файла расписания {save_path}")
