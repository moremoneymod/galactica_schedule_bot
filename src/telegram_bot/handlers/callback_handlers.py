import aiogram.types
from aiogram import Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
import json

from src.core.database.database import read_groups, read_schedule
from utils import utils
from pathlib import Path
# from src.core.database.database import read_schedule, read_groups
from src.telegram_bot.keyboards.keyboards_for_handlers import *
import asyncio

router = Router()




@router.callback_query(F.data == "select_type")
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    keyboard_for_study_type = create_keyboard_for_study_type()
    await callback_query.message.edit_text("~~~ Просмотр расписания ~~~",
                                           reply_markup=keyboard_for_study_type)


@router.callback_query(F.data == "full_time")
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    study_groups = await read_groups(group_type="full_time")
    keyboard_for_full_time_study_groups = create_keyboard_for_study_groups(study_groups)
    await callback_query.message.edit_text("~~~ Выберите группу ~~~",
                                           reply_markup=keyboard_for_full_time_study_groups)


@router.callback_query(F.data == "part_time")
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    study_groups = await read_groups(group_type="part_time")
    keyboard_for_part_time_study_groups = create_keyboard_for_study_groups(study_groups)
    await callback_query.message.edit_text("~~~ Выберите группу ~~~",
                                           reply_markup=keyboard_for_part_time_study_groups)

@router.callback_query(F.data.startswith('ftgroup_'))
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    await callback_query.message.delete()
    group = callback_query.data.replace('ftgroup_', '')
    study_days = ["понедельник", "вторник", "среда", "четверг", "пятница"]
    keyboard_for_study_days = create_keyboard_for_study_days(study_days=study_days, study_group=group,
                                                             study_type="ftgr_")
    await callback_query.message.answer("~~~ Выберите день недели ~~~",
                                        reply_markup=keyboard_for_study_days)


@router.callback_query(F.data.startswith('ptgroup_'))
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    await callback_query.message.delete()
    group = callback_query.data.replace('ptgroup_', '')
    study_days = ["четверг", "пятница", "суббота"]
    keyboard_for_study_days = create_keyboard_for_study_days(study_days=study_days, study_group=group,
                                                             study_type="ptgr_")
    await callback_query.message.answer("~~~ Выберите день недели ~~~",
                                        reply_markup=keyboard_for_study_days)


@router.callback_query(F.data.startswith("ftgr_"))
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    callback_data = callback_query.data.split("!")
    study_group = callback_data[0].replace("ftgr_", '')
    study_day = callback_data[1].replace("d_", '')

    lessons = await read_schedule(group_name=study_group, study_type="full_time", week_day=study_day)

    message = utils.create_lessons_message(study_day, lessons)

    keyboard_for_current_day = create_keyboard_for_selected_study_day(callback_data=f"ftgroup_{study_group}")

    await callback_query.message.edit_text(message, reply_markup=keyboard_for_current_day)


@router.callback_query(F.data.startswith("ptgr_"))
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    callback_data = callback_query.data.split("!")
    study_group = callback_data[0].replace("ptgr_", '')
    study_day = callback_data[1].replace("d_", '')

    lessons = await read_schedule(group_name=study_group, study_type="part_time", week_day=study_day)

    message = utils.create_lessons_message(study_day, lessons)

    keyboard_for_current_day = create_keyboard_for_selected_study_day(callback_data=f"ptgroup_{study_group}")

    await callback_query.message.edit_text(message, reply_markup=keyboard_for_current_day)
