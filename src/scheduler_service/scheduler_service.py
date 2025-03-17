import asyncio
import datetime
import logging

import apscheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.base.broker_client import BrokerClient
from src.config import config

from src.telegram_bot.utils.utils import configure_logging

configure_logging()

logger = logging.getLogger(__name__)


class SchedulerClient(BrokerClient):
    def __init__(self, scheduler):
        super().__init__()
        self.scheduler = scheduler
        self.scheduler.start()

    async def on_message(self, message):
        print(message.body)
        if message.body == b'bot_online':
            try:
                self.scheduler.remove_job('1')
            except apscheduler.jobstores.base.JobLookupError:
                pass
            await self.send_message(b'Update_schedule_now', routing_key='schedule_update_queue1',
                                    exchange=self.exchange_name)
        if message.body == b'schedule_update_is_done':
            try:
                self.scheduler.add_job(self.send_message, 'date',
                                       run_date=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
                                           seconds=20),
                                       args=[b'Update_schedule_now', 'schedule_update_queue1', self.exchange_name], id='1')
            except apscheduler.jobstores.base.ConflictingIdError:
                pass
        await message.channel.basic_ack(
            message.delivery.delivery_tag
        )

    async def exit(self):
        logger.info('Закрытие соединения')
        await self.channel.queue_purge(self.queue)
        await self.connection.close()
        self.scheduler.shutdown()


async def main():
    scheduler = AsyncIOScheduler(timezone='utc')
    client = SchedulerClient(scheduler)
    try:
        await client.connect(broker_url=config.BROKER_URL, exchange_name=config.BROKER_SCHEDULER_EXCHANGE,
                             queue=config.BROKER_SCHEDULER_QUEUE)
        await client.listen_messages()
        while True:
            await asyncio.sleep(1)
    except asyncio.exceptions.CancelledError:
        await client.exit()


if __name__ == '__main__':
    asyncio.run(main())
