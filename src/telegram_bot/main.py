import asyncio
import logging
import psutil
from multiprocessing import set_start_method
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from handlers import handlers, callback_handlers
from src.core.link_parser import LinkParser
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config import config
from src.telegram_bot.utils.utils import update_complete
from src.telegram_bot.middlewares.middleware import DBUpdateMiddlewareCallbackQuery, DBUpdateMiddlewareMessage
from src.telegram_bot.utils.utils import configure_logging
from src.base.broker_client import BrokerClient

logger = logging.getLogger(__name__)

bot = Bot(token=config.TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(handlers.router)
dp.include_router(callback_handlers.router)

dp.message.middleware(DBUpdateMiddlewareMessage())
dp.callback_query.middleware(DBUpdateMiddlewareCallbackQuery())
link_parser = LinkParser()

scheduler = AsyncIOScheduler(timezone='utc')


async def start_bot(client):
    await client.send_message(b'bot_online', exchange='schedule_update_messages', routing_key=client.queue)


class TgBotClient(BrokerClient):
    def __init__(self, update_complete):
        super().__init__()
        self.update_complete = update_complete

    async def on_message(self, message):
        print(message.body)
        if message.body == b'prepare_for_schedule_update':
            self.update_complete.clear()
        if message.body == b'schedule_update_is_done':
            self.update_complete.set()
        await message.channel.basic_ack(
            message.delivery.delivery_tag
        )

    async def exit(self):
        print('Закрытие соединения')
        await self.channel.queue_purge(self.queue)
        await self.connection.close()


async def main():
    p = psutil.Process()
    p.cpu_affinity([0])
    client = TgBotClient(update_complete)
    try:
        await client.connect(broker_url=config.BROKER_URL, exchange_name=config.BROKER_TG_BOT_EXCHANGE,
                             queue=config.BROKER_TG_BOT_QUEUE)
        await start_bot(client)
        await asyncio.gather(dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types()),
                             client.listen_messages())
    except asyncio.exceptions.CancelledError:
        await client.exit()


if __name__ == "__main__":
    set_start_method('spawn')
    asyncio.run(main())
