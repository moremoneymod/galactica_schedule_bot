import os
import aiogram.types
from aiogram import Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
import asyncio
import json
from utils import utils
from pathlib import Path
from aiogram.filters import StateFilter

router = Router()


@router.callback_query(F.data == "select_type")
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    builder = InlineKeyboardBuilder()
    builder.button(text="Очная форма обучения", callback_data="ochnaya")
    builder.button(text="Заочная форма обучения", callback_data="zaochnaya")
    builder.adjust(1, 1)
    await callback_query.message.edit_text("~~~ Просмотр расписания ~~~", reply_markup=builder.as_markup())


@router.callback_query(F.data == "ochnaya")
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    try:
        with open(os.path.split(os.path.dirname(__file__))[0] + '/../files/groups.json', encoding='cp1251') as file:
            print(os.path.split(os.path.dirname(__file__))[0] + '/../groups.json')
            study_groups = json.load(file)
    except Exception as e:
        await callback_query.answer("Выполняется обновление расписания, попробуйте позже", show_alert=True)
        return
    builder = InlineKeyboardBuilder()
    for group in study_groups:
        builder.button(text=group, callback_data=f"ogroup_{group}")
    builder.button(text="Назад", callback_data="select_type")
    builder.adjust(1, 1)
    await callback_query.message.edit_text("~~~ Выберите группу ~~~", reply_markup=builder.as_markup())


@router.callback_query(F.data == "zaochnaya")
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    try:
        with open(os.path.split(os.path.dirname(__file__))[0] + '/../files/groups_zaoch.json', encoding='cp1251') as file:
            study_groups = json.load(file)
    except Exception as e:
        await callback_query.answer("Выполняется обновление расписания, попробуйте позже", show_alert=True)
        return
    builder = InlineKeyboardBuilder()
    for group in study_groups:
        builder.button(text=group, callback_data=f"zgroup_{group}")
    builder.button(text="Назад", callback_data="select_type")
    builder.adjust(1, 1)
    await callback_query.message.edit_text("~~~ Выберите группу ~~~", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith('ogroup_'))
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    await callback_query.message.delete()
    group = callback_query.data.replace('ogroup_', '')
    builder = InlineKeyboardBuilder()
    for day in ["понедельник", "вторник", "среда", "четверг", "пятница"]:
        builder.button(text=day, callback_data=f"ogr_{group}!d_{day}")
    builder.button(text="Назад", callback_data="ochnaya")
    builder.adjust(1, 1)
    await callback_query.message.answer("~~~ Выберите день недели ~~~", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith('zgroup_'))
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    await callback_query.message.delete()
    group = callback_query.data.replace('zgroup_', '')
    builder = InlineKeyboardBuilder()
    for day in ["четверг", "пятница", "суббота"]:
        builder.button(text=day, callback_data=f"zgr_{group}!d_{day}")
    builder.button(text="Назад", callback_data="zaochnaya")
    builder.adjust(1, 1)
    await callback_query.message.answer("~~~ Выберите день недели ~~~", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("ogr_"))
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    data = callback_query.data.split("!")
    group = data[0].replace("ogr_", '')
    day = data[1].replace("d_", '')
    course = group.split('-')[1][0]

    with open(os.path.split(os.path.dirname(__file__))[0] + '/../files/schedule.json', 'r', encoding='cp1251') as f:
        lessons_data = json.load(f)

    builder = InlineKeyboardBuilder()
    lessons = lessons_data[group][day]

    with open(os.path.split(os.path.dirname(__file__))[0] + '/../files/time.json', 'r', encoding='UTF-8') as f:
        time_data = json.load(f)

    time = time_data[course]

    message = utils.create_lessons_message(day, lessons, time)

    print(lessons_data[group][day])
    builder.button(text="Назад", callback_data=f"ogroup_{group}")
    builder.adjust(1, 1)
    await callback_query.message.edit_text(message, reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("zgr_"))
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    data = callback_query.data.split("!")
    group = data[0].replace("zgr_", '')
    day = data[1].replace("d_", '')
    course = group.split('-')[1][0]

    with open(os.path.split(os.path.dirname(__file__))[0] + '/../files/schedule_zaoch.json', 'r', encoding='cp1251') as f:
        lessons_data = json.load(f)

    builder = InlineKeyboardBuilder()
    lessons = lessons_data[group][day]

    with open(os.path.split(os.path.dirname(__file__))[0] + '/../files/time.json', 'r', encoding='UTF-8') as f:
        time_data = json.load(f)

    time = time_data[course]

    message = utils.create_lessons_message(day, lessons, time)

    print(lessons_data[group][day])
    builder.button(text="Назад", callback_data=f"zgroup_{group}")
    builder.adjust(1, 1)
    await callback_query.message.edit_text(message, reply_markup=builder.as_markup())