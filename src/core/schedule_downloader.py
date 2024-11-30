import requests
from src.core.interfaces import ScheduleDownloaderInterface


class ScheduleDownloader(ScheduleDownloaderInterface):
    def __init__(self, directory_manager):
        self.directory_manager = directory_manager

    def download_schedule(self, url: str, study_type: str):
        response = requests.get(url)

        file_name = ""

        if study_type == "full_time":
            file_name = "schedule_full_time"
        elif study_type == "part_time":
            file_name = "schedule_part_time"

        extension = url.split('/')[-1].split('.')[-1]

        save_path = f"{self.directory_manager.get_download_directory()}/{file_name}.{extension}"
        print(save_path)

        with open(save_path, "wb") as file:
            file.write(response.content)

        return save_path
