import asyncio
import os
import time
from pathlib import Path
from typing import Iterable
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.core.database.models import Base
from src.core.database.models import Group, Schedule
import logging
import redis.asyncio as redis
from sqlalchemy import select, delete
from src.config import config
import aiofiles
import json

from src.telegram_bot.utils.utils import configure_logging

configure_logging()

DATABASE_URL = f"sqlite+aiosqlite:///{str(Path(__file__).resolve().parents[2])}/core/database/DB.db"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

db_path = str(Path(__file__).resolve().parents[2])

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


def log_function_exceptions(func):
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            logging.error(f'Произошла ошибка во время выполнения функции {func.__name__}: {e}', exc_info=True)

    return wrapper


@log_function_exceptions
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@log_function_exceptions
async def delete_all_data_from_db() -> None:
    async with async_session() as session:
        await session.execute(delete(Schedule))
        await session.execute(delete(Group))

        await session.commit()


@log_function_exceptions
async def clear_redis_cache() -> None:
    await redis_client.flushdb()


async def update_schedule(files: list) -> None:
    try:
        await asyncio.gather(delete_all_data_from_db(), clear_redis_cache())
        await write_groups_to_db(files)
        await write_schedule_to_db(files)
    except Exception as e:
        logging.error(f'Ошибка при выполнении обновления расписания: {e}')
        return


@log_function_exceptions
async def create_study_group_db_object(group_type: str, group_name: str) -> Group:
    return Group(group_type=group_type, name=group_name)


@log_function_exceptions
async def write_study_group_to_db(study_groups, group_type: str) -> None:
    async with async_session() as session:
        for group_name in study_groups:
            group_db_object = await create_study_group_db_object(group_type=group_type, group_name=group_name)
            session.add(group_db_object)
        await session.commit()


@log_function_exceptions
async def write_groups_to_db(files: list) -> None:
    for file in files:
        study_groups = await read_json_async(file_path=file)
        await write_study_group_to_db(study_groups=study_groups, group_type='full_time')


@log_function_exceptions
async def create_schedule_db_object(schedule_type: str, group_name: str, day: str, lesson_number,
                                    lesson_time, lesson_title) -> Schedule:
    return Schedule(schedule_type=schedule_type, group_name=group_name, day=day, lesson_number=lesson_number,
                    lesson_time=lesson_time, lesson_title=lesson_title)


@log_function_exceptions
async def write_group_schedule_in_db(group_name, study_type: str, group_schedule, lessons_time) -> None:
    await write_group_schedule_in_cache(schedule_type=study_type, group_name=group_name,
                                        group_schedule=group_schedule,
                                        lessons_time=lessons_time)
    async with async_session() as session:
        for week_day in group_schedule:
            for lesson_num in group_schedule[week_day]:
                lesson_time = lessons_time[lesson_num]
                lesson_title = group_schedule[week_day][lesson_num]
                schedule_object = await create_schedule_db_object(schedule_type=study_type, group_name=group_name,
                                                                  day=week_day, lesson_number=lesson_num,
                                                                  lesson_time=lesson_time,
                                                                  lesson_title=lesson_title)
                session.add(schedule_object)
        await session.commit()


@log_function_exceptions
async def create_lesson_num_and_time(lesson_num: str, lesson_time: str) -> str:
    return f'{lesson_num} ({lesson_time})'


@log_function_exceptions
async def write_group_schedule_in_cache(schedule_type: str, group_name: str, group_schedule, lessons_time) -> None:
    for week_day in group_schedule:
        schedule_for_week_day = {}
        for lesson_num in group_schedule[week_day]:
            lesson_time = lessons_time[lesson_num]
            lesson_num_and_time = await create_lesson_num_and_time(lesson_num=lesson_num, lesson_time=lesson_time)
            lesson_title = group_schedule[week_day][lesson_num]
            schedule_for_week_day[lesson_num_and_time] = lesson_title

        cache_key = f'schedule:{schedule_type}-{group_name}-{week_day}'
        await redis_client.set(cache_key, json.dumps(schedule_for_week_day))


@log_function_exceptions
async def write_schedule_to_db(files: list) -> None:
    time_file_path = config.ROOT_DIRECTORY + '/files/time.json'
    lessons_time: dict = await read_json_async(time_file_path)

    for file_path in files:
        schedule = await read_json_async(file_path)
        study_type = await get_study_type(file_path)
        for group in schedule:
            course = group.split('-')[1][0]
            await write_group_schedule_in_db(group_name=group, study_type=study_type,
                                             group_schedule=schedule[group],
                                             lessons_time=lessons_time[course])


@log_function_exceptions
async def get_study_type(file_path: str) -> str:
    return file_path.split('_')[-2] + '_time'


@log_function_exceptions
async def read_schedule_from_cache(group_name: str, study_type: str, week_day: str):
    cache_key = f'schedule:{study_type}-{group_name}-{week_day}'
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    else:
        return None


@log_function_exceptions
async def read_schedule_from_db(group_name: str, study_type: str, week_day: str) -> Iterable[Schedule] | None:
    async with async_session() as session:
        data = await session.execute(
            select(Schedule).where(Schedule.group_name == group_name, Schedule.schedule_type == study_type,
                                   Schedule.day == week_day))
        schedule_data = data.scalars().all()
        if len(schedule_data) == 0:
            return None
    return schedule_data


@log_function_exceptions
async def read_schedule(group_name: str, study_type: str, week_day: str) -> dict | None:
    schedule_from_cache = await read_schedule_from_cache(group_name=group_name, study_type=study_type,
                                                         week_day=week_day)
    if schedule_from_cache:
        return schedule_from_cache
    else:
        schedule_data = await read_schedule_from_db(group_name=group_name, study_type=study_type, week_day=week_day)
        if schedule_data is None:
            return None
        schedule_dict = await create_schedule_dict_from_db_data(schedule_data)

        return schedule_dict


@log_function_exceptions
async def create_schedule_dict_from_db_data(schedule_data) -> dict | None:
    if schedule_data is None:
        return None
    schedule_dict = {}
    for row in schedule_data:
        lesson_time = f'{row.lesson_number} ({row.lesson_time})'
        if lesson_time not in schedule_dict:
            schedule_dict[lesson_time] = {}
        schedule_dict[lesson_time] = row.lesson_title

    return schedule_dict


@log_function_exceptions
async def read_groups(group_type: str) -> list | None:
    study_groups = await read_groups_from_db(group_type=group_type)
    if study_groups is None:
        return None
    groups_list = []
    for group in study_groups:
        groups_list.append(group.name)
    return groups_list


@log_function_exceptions
async def read_groups_from_db(group_type: str) -> Iterable[Group] | None:
    async with async_session() as session:
        groups_data = await session.execute(select(Group).where(Group.group_type == group_type))
        study_groups = groups_data.scalars().all()
        if len(study_groups) == 0:
            return None
        else:
            return study_groups


@log_function_exceptions
async def read_json_async(file_path: str):
    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as file:
        content = await file.read()
        return json.loads(content)
