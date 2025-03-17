import asyncio

import aiormq
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler(timezone='utc')


class BrokerClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None
        self.exchange_name = None
        self.queue = None

    async def connect(self, broker_url: str, exchange_name: str, queue: str) -> None:
        self.connection = await aiormq.connect(broker_url)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
        self.exchange_name = exchange_name
        self.queue = queue

    async def send_message(self, message: bytes, routing_key: str, exchange: str) -> None:
        await self.channel.basic_publish(message, exchange=exchange)

    async def listen_messages(self) -> None:
        declare_ok = await self.channel.queue_declare(queue=self.queue, exclusive=False)
        await self.channel.queue_bind(declare_ok.queue, self.exchange_name)
        await self.channel.basic_consume(
            declare_ok.queue, self.on_message
        )

    async def on_message(self, message):
        pass

    async def exit(self):
        pass
