from abc import ABC, abstractmethod
from typing import Dict, List


class ScheduleDownloaderInterface(ABC):
    @abstractmethod
    def download_schedule(self, url: str, study_type: str):
        """Скачивает расписание"""
        pass


class DownloadDirectoryManagerInterface(ABC):
    @abstractmethod
    def get_download_directory(self) -> str:
        """Возвращает путь к директории для скачивания файлов"""
        pass


class ScheduleParserInterface(ABC):
    @abstractmethod
    def parse_schedule(self) -> None:
        """Парсит расписание"""
        pass


class LinkParserInterface(ABC):
    @staticmethod
    @abstractmethod
    def parse_link(url: str):
        """Парсит сайт для поиска ссылки на скачивание расписания"""
        pass


class JSONConverterInterface(ABC):
    @staticmethod
    @abstractmethod
    def convert_dict_to_json(data: Dict):
        pass

    @staticmethod
    @abstractmethod
    def convert_list_to_json(data: List):
        pass


class JSONFileManagerInterface(ABC):
    @staticmethod
    @abstractmethod
    def save_file(json_file, file_name):
        pass
