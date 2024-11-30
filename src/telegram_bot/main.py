import asyncio
import logging

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.background import BackgroundScheduler
from src.telegram_bot import config
from handlers import handlers, callback_handlers
from pathlib import Path

from src.core.link_parser import LinkParser
from src.core.schedule_downloader import ScheduleDownloader
from src.core.directory_manager import DownloadDirectoryManager
from src.core.parser.schedule_manager import ScheduleManager

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(handlers.router)
dp.include_router(callback_handlers.router)

logger = logging.getLogger(__name__)


def update_schedule():
    schedule_links = LinkParser.parse_link(url=config.SCHEDULE_URL)
    directory_manager = DownloadDirectoryManager(base_directory="files")

    downloader = ScheduleDownloader(directory_manager=directory_manager)
    downloader.download_schedule(url=schedule_links[0], study_type="full_time")
    downloader.download_schedule(url=schedule_links[1], study_type="part_time")

    manager = ScheduleManager()

    current_path = str(Path(__file__).resolve().parents[2])

    manager.export_groups_to_json(file_name=current_path + "/files/schedule_full_time.xls", study_type="full_time")
    manager.export_groups_to_json(file_name=current_path + "/files/schedule_part_time.xls", study_type="part_time")

    manager.export_schedule_to_json(file_name=current_path + "/files/schedule_full_time.xls")
    manager.export_schedule_to_json(file_name=current_path + "/files/schedule_part_time.xls")

    logger.info(msg="Расписание успешно обновлено")


async def main():
    scheduler.start()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    storage = MemoryStorage()
    scheduler = BackgroundScheduler(timezone='utc')
    scheduler.add_job(update_schedule, 'interval', seconds=60 * 60 * 24)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
