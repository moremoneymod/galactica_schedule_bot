import aiofiles

from src.core.interfaces import JSONConverterInterface
from src.core.interfaces import JSONFileManagerInterface
from typing import Dict, List, Any, Union, Type
import json


class JSONConverter(JSONConverterInterface):
    @staticmethod
    async def convert_list_to_json(data: List) -> str:
        json_data = json.dumps(data, ensure_ascii=False)
        return json_data

    @staticmethod
    async def convert_dict_to_json(data: Dict) -> str:
        json_data = json.dumps(data, ensure_ascii=False)
        return json_data


class JSONFileManager(JSONFileManagerInterface):
    @staticmethod
    async def save_file(json_file, file_name) -> None:
        async with aiofiles.open(file_name, 'w', encoding="utf-8") as outfile:
            await outfile.write(json_file)
