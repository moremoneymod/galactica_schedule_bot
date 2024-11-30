from src.core.parser.interfaces import ExcelReaderInterface
from xls2xlsx import XLS2XLSX
from openpyxl import load_workbook
import os


class ExcelReader(ExcelReaderInterface):
    def __init__(self, file_path: str):
        self._file_path = file_path
        if file_path.endswith(".xls"):
            self._file_path = self._convert_xls_to_xlsx(file_path)
        self._workbook = load_workbook(self._file_path)
        self._worksheet = self._workbook.worksheets[0]

    def _convert_xls_to_xlsx(self, file_path) -> str:
        xls2xlsx = XLS2XLSX(file_path)
        new_file_path = f"{os.path.splitext(file_path)[0]}.xlsx"
        xls2xlsx.to_xlsx(new_file_path)
        return new_file_path

    def get_worksheet(self):
        return self._worksheet
