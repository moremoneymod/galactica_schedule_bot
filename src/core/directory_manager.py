import os.path
import logging
from pathlib import Path
from src.core.interfaces import DownloadDirectoryManagerInterface

logger = logging.getLogger(__name__)


class DownloadDirectoryManager(DownloadDirectoryManagerInterface):
    def __init__(self, base_directory: str):
        self.base_directory = self._get_project_root_directory(base_directory)

    @staticmethod
    def _get_project_root_directory(directory_name):
        project_root_directory = Path(__file__).resolve().parents[2]
        return os.path.join(project_root_directory, directory_name)

    def _ensure_directory_exists(self):
        if not os.path.exists(self.base_directory):
            os.makedirs(self.base_directory)
            logger.info(f"Создана директория для файлов: {self.base_directory}")
        else:
            logger.info(f"Директория {self.base_directory} уже существует")

    def get_download_directory(self) -> str:
        self._ensure_directory_exists()
        return self.base_directory
