import asyncio
import logging
import sys

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from parser.parser import ScheduleParser
from parser.downloader.downloader import Downloader
import config
from handlers import handlers, callback_handlers
import os
from pathlib import Path

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(handlers.router)
dp.include_router(callback_handlers.router)

downloader = Downloader()


def update_schedule():
    downloader.get_schedule()
    parser1 = ScheduleParser(str(Path(__file__).resolve().parents[1]) + "/parser/downloader/files/schedule.xls")
    parser2 = ScheduleParser(str(Path(__file__).resolve().parents[1]) + "/parser/downloader/files/schedule_zaoch.xls")
    parser1.get_json_schedule(file_name="../files/schedule.json")
    parser2.get_json_schedule(file_name="../files/schedule_zaoch.json")


async def main():
    scheduler.start()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    storage = MemoryStorage()
    scheduler = BackgroundScheduler(timezone='utc')
    scheduler.add_job(update_schedule, 'interval', seconds=3600)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
