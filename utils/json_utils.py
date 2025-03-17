import json


def json_converter(dict_to_convert: dict) -> str:
    json_dict = json.dumps(dict_to_convert, ensure_ascii=False)
    return json_dict


def save_json(json_file: str) -> None:
    with open("schedule.json", 'w') as outfile:
        outfile.write(json_file)
