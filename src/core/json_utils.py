from src.core.interfaces import JSONConverterInterface
from src.core.interfaces import JSONFileManagerInterface
from typing import Dict, List, Any, Union, Type
import json

JSON = Union[Dict[str, Any], List[Any], int, str, float, bool, Type[None]]


class JSONConverter(JSONConverterInterface):
    @staticmethod
    def convert_dict_to_json(data: Dict) -> JSON:
        json_data = json.dumps(data, ensure_ascii=False)
        return json_data

    @staticmethod
    def convert_list_to_json(data: List) -> JSON:
        json_data = json.dumps(data, ensure_ascii=False)
        return json_data


class JSONFileManager(JSONFileManagerInterface):
    @staticmethod
    def save_file(json_file, file_name):
        with open(file_name, 'w', encoding="utf-8") as outfile:
            outfile.write(json_file)
