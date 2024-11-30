import json
from typing import Dict, Union, Any, List, Type

JSON = Union[Dict[str, Any], List[Any], int, str, float, bool, Type[None]]


def json_converter(dict_to_convert: Dict) -> JSON:
    json_dict = json.dumps(dict_to_convert, ensure_ascii=False)
    return json_dict


def save_json(json_file: JSON) -> None:
    with open("schedule.json", 'w') as outfile:
        outfile.write(json_file)
