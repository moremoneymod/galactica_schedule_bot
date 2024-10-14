import json
import time
from typing import Dict, Union, Any, List, Type
JSON = Union[Dict[str, Any], List[Any], int, str, float, bool, Type[None]]


class JSONConverter:
    def __init__(self):
        pass

    @staticmethod
    def convert_dict_to_json(data: Dict) -> JSON:
        json_data = json.dumps(data, ensure_ascii=False)
        return json_data

    @staticmethod
    def convert_list_to_json(data: List) -> JSON:
        json_data = json.dumps(data, ensure_ascii=False)
        return json_data


def json_converter(dict_to_convert: Dict | List) -> JSON:
    json_dict = json.dumps(dict_to_convert, ensure_ascii=False)
    return json_dict


class JSONFileManager:
    def __init__(self):
        pass

    @staticmethod
    def save_file(json_file: JSON, file_name: str, encoding="UTF-8") -> None:
        try:
            with open(file_name, 'w', encoding=encoding) as outfile:
                outfile.write(json_file)
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass


def save_json(json_file: JSON, file_name: str) -> None:
    with open(file_name, 'w', encoding="UTF-8") as outfile:
        outfile.write(json_file)
        time.sleep(10)
