import os
import pathlib
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config:
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    SCHEDULE_URL = os.getenv('SCHEDULE_URL')
    SITE_URL = os.getenv('SITE_URL')
    SCHEDULE_FILES_DIRECTORY = str(os.path.join(Path(__file__).resolve().parents[1], 'files'))
    ROOT_DIRECTORY = str(Path(__file__).resolve().parents[1])
    BROKER_URL = 'amqp://guest:guest@localhost'
    BROKER_SCHEDULER_QUEUE = 'schedule_update_queue'
    BROKER_SCHEDULER_EXCHANGE = 'schedule_update_messages'
    BROKER_SCHEDULE_UPDATER_QUEUE = 'schedule_update_queue1'
    BROKER_SCHEDULE_UPDATER_EXCHANGE = 'schedule_update_messages'
    BROKER_TG_BOT_QUEUE = 'schedule_update_queue2'
    BROKER_TG_BOT_EXCHANGE = 'tg_bot_schedule_update'

config = Config()