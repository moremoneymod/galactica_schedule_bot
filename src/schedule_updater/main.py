import asyncio
import logging
import time
import psutil
from src.core.link_parser import LinkParser
from src.core.schedule_downloader import ScheduleDownloader
from src.core.parser.schedule_manager import ScheduleManager
from src.core.database.database import init_models, update_schedule
from src.config import config
from src.base.broker_client import BrokerClient

logger = logging.getLogger(__name__)
link_parser = LinkParser()
update_lock = asyncio.Lock()


class ScheduleUpdaterClient(BrokerClient):
    async def on_message(self, message) -> None:
        print(message.body)
        if message.body == b'Update_schedule_now':
            logging.info('Начало обновления расписания')
            try:
                await self.send_message(b'prepare_for_schedule_update', exchange=config.BROKER_TG_BOT_EXCHANGE,
                                        routing_key=config.BROKER_TG_BOT_QUEUE)
                await self.send_message(b'prepare_for_schedule_update', exchange=self.exchange_name,
                                        routing_key=self.queue)
            except Exception as e:
                print(e)
            await update_db()
            await self.send_message(b'schedule_update_is_done', exchange=config.BROKER_TG_BOT_EXCHANGE,
                                    routing_key=config.BROKER_TG_BOT_QUEUE)
            await self.send_message(b'schedule_update_is_done', exchange=self.exchange_name,
                                    routing_key=self.queue)
            logging.info('Расписание успешно обновлено')
        await message.channel.basic_ack(
            message.delivery.delivery_tag
        )

    async def exit(self):
        print('Закрытие соединения')
        await self.channel.queue_purge(self.queue)
        await self.connection.close()


async def download_schedule() -> list[str, str] | list[str] | list | None:
    schedule_file_links = []
    try:
        schedule_links = await link_parser.parse_links(url=config.SCHEDULE_URL)
        if schedule_links is None:
            return None

        schedule_link_for_full_time_study = None
        schedule_link_for_part_time_study = None
        if 'full_time' in schedule_links:
            schedule_link_for_full_time_study = schedule_links['full_time']
        if 'part_time' in schedule_links:
            schedule_link_for_part_time_study = schedule_links['part_time']

        downloader = ScheduleDownloader()
        task1, task2 = None, None
        async with asyncio.TaskGroup() as tg:
            if schedule_link_for_full_time_study:
                task1 = tg.create_task(
                    downloader.download_schedule(file_url=schedule_link_for_full_time_study, study_type='full_time'))
            if schedule_link_for_part_time_study:
                task2 = tg.create_task(
                    downloader.download_schedule(file_url=schedule_link_for_part_time_study, study_type='part_time'))

        full_time_schedule_file_path = None
        part_time_schedule_file_path = None
        if task1:
            full_time_schedule_file_path = task1.result()
        if task2:
            part_time_schedule_file_path = task2.result()

        if full_time_schedule_file_path is not None:
            schedule_file_links.append(full_time_schedule_file_path)
        if part_time_schedule_file_path is not None:
            schedule_file_links.append(part_time_schedule_file_path)

        return schedule_file_links
    except Exception as e:
        logger.error(f'Произошла ошибка при попытке скачивания расписания {e}')
        return None


async def convert_data_to_json(file_links: list) -> list:
    file_path = []
    schedule_manager = ScheduleManager()
    for file_link in file_links:
        await schedule_manager.export_groups_to_json(file_name=file_link)
        schedule_file_path = await schedule_manager.export_schedule_to_json(file_name=file_link)
        file_path.append(schedule_file_path)
    return file_path


async def update_schedule_in_db():
    try:
        file_links = await download_schedule()
        json_file_links = await convert_data_to_json(file_links=file_links)
        await update_schedule(files=json_file_links)
    except Exception as e:
        logging.error(f'Ошибка при обновлении расписания: {e}', exc_info=True)


async def update_db():
    logging.info(f'start update db at {time.time()}')
    try:
        async with update_lock:
            await init_models()
    except Exception as e:
        logging.error(f'Ошибка при инициализации моделей: {e}', exc_info=True)
        return
    try:
        async with update_lock:
            await update_schedule_in_db()
    except Exception as e:
        logging.error(f'Ошибка при обновлении расписания: {e}', exc_info=True)
    finally:
        logging.info(f'end of update db at {time.time()}')


async def main():
    client = ScheduleUpdaterClient()
    try:
        await client.connect(broker_url=config.BROKER_URL, exchange_name=config.BROKER_SCHEDULE_UPDATER_EXCHANGE,
                             queue=config.BROKER_SCHEDULE_UPDATER_QUEUE)
        await client.listen_messages()
        while True:
            await asyncio.sleep(1)
    except asyncio.exceptions.CancelledError:
        await client.exit()


if __name__ == "__main__":
    p = psutil.Process()
    p.cpu_affinity([1])
    asyncio.run(main())
