from src.core.parser.interfaces import ScheduleParserInterface
import re
from typing import List, Dict, Any


class ScheduleParser(ScheduleParserInterface):
    def __init__(self, worksheet) -> None:
        self._worksheet = worksheet

    def _get_group_row_index(self) -> int:
        group_row_index = 0
        for row in self._worksheet.iter_rows():
            group_row_index += 1
            for cell in row:
                if cell.value is not None:
                    cell_value = str(cell.value)
                    if re.match(r'^[А-Яа-я]{1,3} - \d{2}', cell_value) is not None:
                        return group_row_index

    def _get_study_groups_column_coordinates(self) -> list[int]:
        groups_row_index = self._get_group_row_index()
        study_group_coordinates = []
        for cell in self._worksheet[groups_row_index]:
            if cell.value is None or cell.value.count('-') == 0:
                continue
            else:
                study_group_coordinates.append(cell.column)
        return study_group_coordinates

    def _get_lessons_row_index(self, group_row_index) -> int:
        group_columns = self._get_study_groups_column_coordinates()
        next_cell = self._worksheet.cell(group_row_index + 1, group_columns[0] - 1)
        if next_cell.value is None:
            return group_row_index + 2
        else:
            return group_row_index + 1

    def _end_of_sheet_index(self) -> int:
        last_row_index = self._get_lessons_row_index(self._get_group_row_index())

        for row in self._worksheet.iter_rows(min_row=last_row_index + 1):
            flag = False
            for cell in row:
                if cell.value is not None:
                    flag = True
            if flag is True:
                last_row_index += 1
            else:
                return last_row_index

    def _get_study_groups(self) -> list[str]:
        study_groups_row_index = self._get_group_row_index()
        study_groups = []
        sheet = self._worksheet
        study_groups_column_coordinates = self._get_study_groups_column_coordinates()
        for column_index in study_groups_column_coordinates:
            cell_value = str(sheet.cell(study_groups_row_index, column_index).value)
            if cell_value.count('-') < 1:
                continue
            group_name_value = cell_value
            group_name = self._format_study_group_name(group_name=group_name_value)
            study_groups.append(group_name)
        return study_groups

    def _get_row_coordinates_for_subjects(self) -> list:
        sheet = self._worksheet
        lesson_numbers_column_coordinate = self._get_study_days_column_coordinate()
        start_index = self._get_group_row_index() + 1
        if sheet.cell(start_index, lesson_numbers_column_coordinate).value is None:
            start_index += 1
        last_row_index = self._end_of_sheet_index()
        return [row_index for row_index in range(start_index, last_row_index + 1)]

    def _get_study_days_and_their_row_indexes(self) -> dict:
        start_row_index = self._get_group_row_index() + 1
        column_index_of_week_days = self._get_study_groups_column_coordinates()[0] - 2
        last_row_index = self._end_of_sheet_index() + 1

        study_days_and_their_row_index = {}
        for row in range(start_row_index, last_row_index):
            cell = self._worksheet.cell(row, column_index_of_week_days)
            if cell.value is None:
                continue
            else:
                study_day = self._format_study_day(study_day=cell.value)
                study_days_and_their_row_index[cell.row] = study_day
        return study_days_and_their_row_index

    @staticmethod
    def _format_study_day(study_day: str) -> str:
        return study_day.strip()

    def _get_study_days_column_coordinate(self) -> int:
        group_column_coordinates = self._get_study_groups_column_coordinates()
        return group_column_coordinates[0] - 1

    def _read_column(self, col_index: int, row_indexes, days_and_their_indexes) -> dict:
        group_row_index = self._get_group_row_index()
        study_days_column_coordinate = self._get_study_days_column_coordinate()

        sheet = self._worksheet
        current_day = ''
        schedule_for_this_column = {}

        study_group = sheet.cell(group_row_index, col_index).value
        study_group = self._format_study_group_name(group_name=study_group)
        schedule_for_this_column[study_group] = {}
        for row_index in row_indexes:

            cell = sheet.cell(row_index, col_index)
            subject_name_value = cell.value
            lesson_time_value = int(sheet.cell(cell.row, study_days_column_coordinate).value)

            if cell.value is None and int(sheet.cell(row_index, study_days_column_coordinate).value) % 2 != 0:
                subject_name_value = "Нет пары"
            elif cell.value is None:
                continue

            if row_index in days_and_their_indexes:
                current_day = days_and_their_indexes[row_index]

            subject_name = self._format_subject_name(subject_name=subject_name_value)
            lesson_time = self._format_lesson_time(lesson_time=lesson_time_value)

            if current_day not in schedule_for_this_column[study_group]:
                schedule_for_this_column[study_group][current_day] = {}

            schedule_for_this_column[study_group][current_day][lesson_time] = subject_name
        return schedule_for_this_column

    @staticmethod
    def _format_study_group_name(group_name: str) -> str:
        formatted_group_name = group_name
        if formatted_group_name.count('-') > 1:
            if formatted_group_name.count(',') == 0:
                formatted_group_name = re.sub('  +', ',', formatted_group_name)
            formatted_group_name = formatted_group_name.replace(' ', '')
            formatted_group_name = formatted_group_name.replace(',', ", ")
        else:
            formatted_group_name = formatted_group_name.replace(' ', '')
        return formatted_group_name

    @staticmethod
    def _format_subject_name(subject_name: str) -> str:
        return re.sub(" +", " ", subject_name.strip())

    @staticmethod
    def _format_lesson_time(lesson_time: int) -> str:
        formated_lesson_time = f"{lesson_time}-{lesson_time + 1} урок"
        return formated_lesson_time

    def _read_columns_in_list(self) -> list:
        study_days_and_their_row_indexes = self._get_study_days_and_their_row_indexes()
        row_indexes = self._get_row_coordinates_for_subjects()
        column_indexes = self._get_study_groups_column_coordinates()

        schedule_in_rows = []

        for column_index in column_indexes:
            study_in_row = self._read_column(col_index=column_index, row_indexes=row_indexes,
                                             days_and_their_indexes=study_days_and_their_row_indexes)
            schedule_in_rows.append(study_in_row)
        return schedule_in_rows

    @staticmethod
    def _create_schedule_dict_from_list(schedule_in_list) -> dict:
        schedule = {}
        for group_schedule in schedule_in_list:
            study_group = list(group_schedule.keys())[0]
            schedule[study_group] = group_schedule[study_group]
        return schedule

    @staticmethod
    def _format_day(day: str) -> str:
        formatted_day = day.split(',')[0]
        return formatted_day

    def parse_schedule(self) -> dict:
        schedule_in_list = self._read_columns_in_list()
        schedule = self._create_schedule_dict_from_list(schedule_in_list=schedule_in_list)
        self._get_study_groups()
        return schedule
