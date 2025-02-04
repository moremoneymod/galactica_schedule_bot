import asyncio
import json
from pathlib import Path
from typing import Iterable

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from src.core.database.models import Base
from src.core.database.models import Group, Schedule
from sqlalchemy.ext.declarative import declarative_base
import logging
import redis.asyncio as redis

from sqlalchemy import select, delete, Sequence

logger = logging.getLogger(__name__)

DATABASE_URL = f"sqlite+aiosqlite:///{str(Path(__file__).resolve().parents[2])}/core/database/DB.db"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

db_path = str(Path(__file__).resolve().parents[2])

redis_client = redis.Redis(host="localhost", port=6379, db=0)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def delete_all_data_from_db() -> None:
    async with async_session() as session:
        await session.execute(delete(Schedule))
        await session.execute(delete(Group))
        await session.commit()


async def update_schedule() -> None:
    await delete_all_data_from_db()
    await write_groups_to_db()


async def create_study_group_db_object(group_type: str, group_name: str) -> Group:
    return Group(group_type=group_type, name=group_name)


def log_function_call(func):
    async def wrapper(*args, **kwargs):
        logger.info(f"Вызов функции {func.__name__} с аргументами: {args}, {kwargs}")
        try:
            result = await func(*args, **kwargs)
            logger.info(f"Функция {func.__name__} завершена успешно")
            return result
        except Exception as e:
            logging.error(f"Ошибка при выполнении функции {func.__name__}: {e}", exc_info=True)
            raise

    return wrapper


@log_function_call
async def read_study_groups_from_json(file_path: str):
    with open(file_path, encoding='utf-8') as file:
        study_groups = json.load(file)
    return study_groups


@log_function_call
async def write_study_group_to_db(study_groups, group_type: str):
    async with async_session() as session:
        for group_name in study_groups:
            group_db_object = await create_study_group_db_object(group_type=group_type, group_name=group_name)
            session.add(group_db_object)
        await session.commit()


@log_function_call
async def write_groups_to_db() -> None:
    root_path = str(Path(__file__).resolve().parents[3])

    print(f"Ping successful: {await redis_client.ping()}")
    await redis_client.aclose()

    full_time_study_groups_path = root_path + "/files/groups_full_time.json"
    part_time_study_groups_path = root_path + "/files/groups_full_time.json"

    study_groups_full_time = await read_study_groups_from_json(file_path=full_time_study_groups_path)
    study_groups_part_time = await read_study_groups_from_json(file_path=part_time_study_groups_path)

    await write_study_group_to_db(study_groups=study_groups_full_time, group_type="full_time")
    await write_study_group_to_db(study_groups=study_groups_part_time, group_type="part_time")


@log_function_call
async def read_schedule_from_json(file_path: str):
    with open(file_path, encoding="utf-8") as file:
        schedule = json.load(file)
    return schedule


@log_function_call
async def read_lessons_time_from_json(file_path: str):
    with open(file_path, encoding="utf-8") as file:
        time = json.load(file)
    return time


@log_function_call
async def create_schedule_db_object(schedule_type: str, group_name: str, day: str, lesson_number,
                                    lesson_time, lesson_title):
    return Schedule(schedule_type=schedule_type, group_name=group_name, day=day, lesson_number=lesson_number,
                    lesson_time=lesson_time, lesson_title=lesson_title)


@log_function_call
async def write_group_schedule_in_db(group_name, study_type: str, group_schedule, lessons_time):
    async with async_session() as session:
        for week_day in group_schedule:
            await write_group_schedule_in_cache(schedule_type=study_type, group_name=group_name, day=week_day,
                                                schedule_data=group_schedule[week_day])
            for lesson_num in group_schedule[week_day]:
                lesson_time = lessons_time[lesson_num]
                lesson_title = group_schedule[week_day][lesson_num]
                schedule_object = await create_schedule_db_object(schedule_type=study_type, group_name=group_name,
                                                                  day=week_day, lesson_number=lesson_num,
                                                                  lesson_time=lesson_time, lesson_title=lesson_title)
                session.add(schedule_object)
        await session.commit()


@log_function_call
async def write_group_schedule_in_cache(schedule_type: str, group_name: str, day: str, schedule_data):
    cache_key = f"schedule:{schedule_type}-{group_name}-{day}"
    await redis_client.set(cache_key, json.dumps(schedule_data))


@log_function_call
async def write_schedule_to_db() -> None:
    root_path = str(Path(__file__).resolve().parents[3])

    schedule_full_time_file_path = root_path + "/files/schedule_full_time.json"
    schedule_part_time_file_path = root_path + "/files/schedule_part_time.json"

    schedule_full_time = await read_schedule_from_json(file_path=schedule_full_time_file_path)
    schedule_part_time = await read_schedule_from_json(file_path=schedule_part_time_file_path)

    time_file_path = root_path + "/files/time.json"
    lessons_time = await read_lessons_time_from_json(file_path=time_file_path)

    for group in schedule_full_time:
        course = group.split('-')[1][0]
        await write_group_schedule_in_db(group_name=group, study_type="full_time",
                                         group_schedule=schedule_full_time[group], lessons_time=lessons_time[course])

    for group in schedule_part_time:
        course = group.split('-')[1][0]
        await write_group_schedule_in_db(group_name=group, study_type="part_time",
                                         group_schedule=schedule_part_time[group], lessons_time=lessons_time[course])


@log_function_call
async def read_schedule_from_cache(group_name: str, study_type: str, week_day: str):
    cache_key = f"schedule:{study_type}-{group_name}-{week_day}"
    cached_data = await redis_client.get(cache_key)

    if cached_data:
        return json.loads(cached_data)
    else:
        return None


@log_function_call
async def read_schedule_from_db(group_name: str, study_type: str, week_day: str) -> Iterable[Schedule] | None:
    async with async_session() as session:
        data = await session.execute(
            select(Schedule).where(Schedule.group_name == group_name, Schedule.schedule_type == study_type,
                                   Schedule.day == week_day))
        schedule_data = data.scalars().all()
        if len(schedule_data) == 0:
            return None
    return schedule_data


@log_function_call
async def read_schedule(group_name: str, study_type: str, week_day: str) -> dict:
    schedule_from_cache = await read_schedule_from_cache(group_name=group_name, study_type=study_type,
                                                         week_day=week_day)
    if schedule_from_cache:
        return schedule_from_cache
    else:
        schedule_data = await read_schedule_from_db(group_name=group_name, study_type=study_type, week_day=week_day)
        schedule_dict = await create_schedule_dict_from_db_data(schedule_data)

        return schedule_dict


@log_function_call
async def create_schedule_dict_from_db_data(schedule_data) -> dict | None:
    if schedule_data is None:
        return None
    schedule_dict = {}
    for row in schedule_data:
        lesson_time = f"{row.lesson_number} ({row.lesson_time})"
        if lesson_time not in schedule_dict:
            schedule_dict[lesson_time] = {}
        schedule_dict[lesson_time] = row.lesson_title

    return schedule_dict


@log_function_call
async def read_groups(group_type: str) -> list | None:
    study_groups = await read_groups_from_db(group_type=group_type)
    if study_groups is None:
        return None
    groups_list = []
    for group in study_groups:
        groups_list.append(group.name)
    return groups_list


@log_function_call
async def read_groups_from_db(group_type: str) -> Iterable[Group] | None:
    async with async_session() as session:
        groups_data = await session.execute(select(Group).where(Group.group_type == group_type))
        study_groups = groups_data.scalars().all()
        if len(study_groups) == 0:
            return None
        else:
            return study_groups
