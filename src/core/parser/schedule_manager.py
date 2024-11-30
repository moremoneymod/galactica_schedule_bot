import os.path

from src.core.parser.excel_reader import ExcelReader
from src.core.parser.schedule_parser import ScheduleParser
from src.core.json_utils import JSONConverter, JSONFileManager
from pathlib import Path


class ScheduleManager:
    def __init__(self):
        # self.excel_reader = excel_reader
        # self.converter = converter
        # self.file_manager = file_manager
        self.root_directory = Path(__file__).resolve().parents[2]

    def export_schedule_to_json(self, file_name):
        worksheet = ExcelReader(file_path=file_name).get_worksheet()
        schedule = ScheduleParser(worksheet).parse_schedule()
        json_schedule = JSONConverter.convert_dict_to_json(schedule)
        new_file_name = f"{os.path.splitext(file_name)[0]}.json"
        JSONFileManager.save_file(json_schedule, new_file_name)

    def export_groups_to_json(self, file_name, study_type):
        worksheet = ExcelReader(file_path=file_name).get_worksheet()
        groups = ScheduleParser(worksheet).get_groups()
        json_groups = JSONConverter.convert_list_to_json(groups)
        new_file_name = f"{Path(__file__).resolve().parents[3]}/files/groups_{study_type}.json"
        JSONFileManager.save_file(json_groups, new_file_name)
