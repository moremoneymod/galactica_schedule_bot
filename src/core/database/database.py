import asyncio
import json
from pathlib import Path

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from models import Base
from models import Group, Schedule
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import Session

DATABASE_URL = "sqlite+aiosqlite:///./DB.db"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(init_models())

groups = []


async def test():
    root_path = str(Path(__file__).resolve().parents[3])
    with open(root_path + '/files/groups_full_time.json', encoding='utf-8') as f:
        print(f.readlines())


# async def add():
#     async with async_session() as session:
#         new_group = Group(group_id=1, name="ст-11у")
#         session.add(new_group)
#         await session.commit()


async def write_groups_to_db():
    root_path = str(Path(__file__).resolve().parents[3])

    try:
        with open(root_path + "/files/groups_full_time.json", encoding='utf-8') as file:
            print(root_path + "/files/groups_full_time.json")
            study_groups_full_time = json.load(file)
        with open(root_path + "/files/groups_part_time.json", encoding='utf-8') as file:
            print(root_path + "/files/groups_part_time.json")
            study_groups_part_time = json.load(file)
    except Exception as e:
        print(f"Ошибка при чтении файла - {e}")
        return
    print(study_groups_full_time)
    print(study_groups_part_time)
    async with async_session() as session:
        for group in study_groups_full_time:
            new_group = Group(group_type="full_time", name=group)
            session.add(new_group)
        for group in study_groups_part_time:
            new_group = Group(group_type="part_time", name=group)
            session.add(new_group)
        await session.commit()


async def write_schedule_to_db():
    root_path = str(Path(__file__).resolve().parents[3])

    try:
        with open(root_path + "/files/schedule_full_time.json", encoding='utf-8') as file:
            schedule_full_time = json.load(file)
        print(schedule_full_time)

    except Exception as e:
        print(f"Произошла ошибка во время чтения расписания - {e}")
        return
    async with async_session() as session:
        schedule_type = "full_time"
        for group in schedule_full_time:
            for day in schedule_full_time[group]:
                for lesson in schedule_full_time[group][day]:
                    lesson_title = schedule_full_time[group][day][lesson]
                    new_schedule = Schedule(schedule_type=schedule_type, group_name=group, day=day,
                                            lesson_number=lesson, lesson_time="",
                                            lesson_title=lesson_title)
                    session.add(new_schedule)
        await session.commit()


# asyncio.run(add())
asyncio.run(test())
asyncio.run(write_groups_to_db())
asyncio.run(write_schedule_to_db())
