import aiogram.types
from aiogram import Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
import json
from utils import utils
from pathlib import Path

router = Router()


@router.callback_query(F.data == "select_type")
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    builder = InlineKeyboardBuilder()
    builder.button(text="Очная форма обучения", callback_data="full_time")
    builder.button(text="Заочная форма обучения", callback_data="part_time")
    builder.adjust(1, 1)
    await callback_query.message.edit_text("~~~ Просмотр расписания ~~~", reply_markup=builder.as_markup())


@router.callback_query(F.data == "full_time")
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    root_path = str(Path(__file__).resolve().parents[3])

    try:
        with open(root_path + "/files/groups_full_time.json", encoding='utf-8') as file:
            print(root_path + "/files/groups_full_time.json")
            study_groups = json.load(file)
    except Exception as e:
        await callback_query.answer("Выполняется обновление расписания, попробуйте позже", show_alert=True)
        return
    builder = InlineKeyboardBuilder()
    for group in study_groups:
        builder.button(text=group, callback_data=f"ftgroup_{group}")
    builder.button(text="Назад", callback_data="select_type")
    builder.adjust(1, 1)
    await callback_query.message.edit_text("~~~ Выберите группу ~~~", reply_markup=builder.as_markup())


@router.callback_query(F.data == "part_time")
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    root_path = str(Path(__file__).resolve().parents[3])

    try:
        with open(root_path + "/files/groups_part_time.json", encoding='utf-8') as file:
            print(root_path + "/files/groups_part_time.json")
            study_groups = json.load(file)
    except Exception as e:
        await callback_query.answer("Выполняется обновление расписания, попробуйте позже", show_alert=True)
        return
    builder = InlineKeyboardBuilder()
    for group in study_groups:
        builder.button(text=group, callback_data=f"ptgroup_{group}")
    builder.button(text="Назад", callback_data="select_type")
    builder.adjust(1, 1)
    await callback_query.message.edit_text("~~~ Выберите группу ~~~", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith('ftgroup_'))
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    await callback_query.message.delete()
    group = callback_query.data.replace('ftgroup_', '')
    builder = InlineKeyboardBuilder()
    for day in ["понедельник", "вторник", "среда", "четверг", "пятница"]:
        builder.button(text=day, callback_data=f"ftgr_{group}!d_{day}")
    builder.button(text="Назад", callback_data="full_time")
    builder.adjust(1, 1)
    await callback_query.message.answer("~~~ Выберите день недели ~~~", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith('ptgroup_'))
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    await callback_query.message.delete()
    group = callback_query.data.replace('ptgroup_', '')
    builder = InlineKeyboardBuilder()
    for day in ["четверг", "пятница", "суббота"]:
        builder.button(text=day, callback_data=f"ptgr_{group}!d_{day}")
    builder.button(text="Назад", callback_data="part_time")
    builder.adjust(1, 1)
    await callback_query.message.answer("~~~ Выберите день недели ~~~", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("ftgr_"))
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    data = callback_query.data.split("!")
    group = data[0].replace("ftgr_", '')
    day = data[1].replace("d_", '')
    course = group.split('-')[1][0]

    root_path = str(Path(__file__).resolve().parents[3])
    builder = InlineKeyboardBuilder()

    try:
        with open(root_path + "/files/schedule_full_time.json", 'r', encoding='utf-8') as f:
            lessons_data = json.load(f)

        if day in lessons_data[group]:
            lessons = lessons_data[group][day]
        else:
            lessons = None

        with open(root_path + "/files/time.json", 'r', encoding='utf-8') as f:
            time_data = json.load(f)

        time = time_data[course]

        message = utils.create_lessons_message(day, lessons, time)

        builder.button(text="Назад", callback_data=f"ftgroup_{group}")
        builder.adjust(1, 1)
        await callback_query.message.edit_text(message, reply_markup=builder.as_markup())

    except Exception as e:
        await callback_query.message.answer(text="Возникли проблемы при чтении расписания")


@router.callback_query(F.data.startswith("ptgr_"))
async def callback_query_handler(callback_query: aiogram.types.CallbackQuery) -> None:
    data = callback_query.data.split("!")
    group = data[0].replace("ptgr_", '')
    day = data[1].replace("d_", '')
    course = group.split('-')[1][0]

    root_path = str(Path(__file__).resolve().parents[3])
    builder = InlineKeyboardBuilder()

    try:
        with open(root_path + "/files/schedule_part_time.json", 'r', encoding='utf-8') as f:
            lessons_data = json.load(f)

        if day in lessons_data[group]:
            lessons = lessons_data[group][day]
        else:
            lessons = None

        with open(root_path + "/files/time.json", 'r', encoding='utf-8') as f:
            time_data = json.load(f)

        time = time_data[course]

        message = utils.create_lessons_message(day, lessons, time)

        builder.button(text="Назад", callback_data=f"ptgroup_{group}")
        builder.adjust(1, 1)
        await callback_query.message.edit_text(message, reply_markup=builder.as_markup())

    except Exception as e:
        await callback_query.message.answer(text="Возникли проблемы при чтении расписания")
