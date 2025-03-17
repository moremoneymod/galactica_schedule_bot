import asyncio
import logging
import time

from src.core.parser.interfaces import ExcelReaderInterface
from xls2xlsx import XLS2XLSX
from openpyxl import load_workbook
import os

from src.telegram_bot.utils.utils import configure_logging

configure_logging()

logger = logging.getLogger(__name__)


class ExcelReader(ExcelReaderInterface):
    def __init__(self, file_path: str):
        self._file_path = file_path
        self._workbook = None
        self._worksheet = None

    async def _initialize(self) -> None:
        try:
            if self._file_path.endswith('.xls'):
                self._file_path = await self._convert_xls_to_xlsx(self._file_path)
            self._workbook = load_workbook(self._file_path)
            self._worksheet = self._workbook.worksheets[0]
        except Exception as e:
            self._worksheet = None
            logging.error(f'Произошла ошибка при инициализации ExcelReader - {e}')

    @staticmethod
    async def _convert_xls_to_xlsx(file_path) -> str:
        xls2xlsx = XLS2XLSX(file_path)
        new_file_path = f'{os.path.splitext(file_path)[0]}.xlsx'
        xls2xlsx.to_xlsx(new_file_path)
        return new_file_path

    async def get_worksheet(self):
        if self._worksheet is None:
            await self._initialize()
        return self._worksheet
