import os.path
import time

from src.core.parser.excel_reader import ExcelReader
from src.core.parser.schedule_parser import ScheduleParser
from src.core.json_utils import JSONConverter, JSONFileManager
from src.config import config


class ScheduleManager:

    @staticmethod
    async def export_schedule_to_json(file_name: str) -> str | None:
        worksheet = await ExcelReader(file_path=file_name).get_worksheet()
        if worksheet is None:
            return None
        schedule: dict = await ScheduleParser(worksheet).parse_schedule()
        json_schedule: str = await JSONConverter.convert_dict_to_json(schedule)
        json_file_name = f'{os.path.splitext(file_name)[0]}.json'
        await JSONFileManager.save_file(json_schedule, json_file_name)
        return json_file_name

    @staticmethod
    async def export_groups_to_json(file_name: str) -> str | None:
        study_type = file_name.split('_')[-2]
        worksheet = await ExcelReader(file_path=file_name).get_worksheet()
        if worksheet is None:
            return None
        groups: list[str] = await ScheduleParser(worksheet).get_study_groups()
        json_groups: str = await JSONConverter.convert_list_to_json(groups)
        json_file_name = f'{config.SCHEDULE_FILES_DIRECTORY}\\groups_{study_type}_time.json'
        await JSONFileManager.save_file(json_groups, json_file_name)
        return json_file_name
