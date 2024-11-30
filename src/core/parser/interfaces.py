from abc import ABC, abstractmethod
from typing import Dict, List


class ScheduleParserInterface(ABC):
    @abstractmethod
    def parse_schedule(self):
        pass


class ExcelReaderInterface(ABC):
    @abstractmethod
    def get_worksheet(self):
        pass
