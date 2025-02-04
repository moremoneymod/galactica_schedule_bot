from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from src.telegram_bot.keyboards.keyboards_for_handlers import create_keyboard_for_study_type

router = Router()



@router.message(Command('start'))
async def command_start_handler(message: Message) -> None:
    await message.answer("Данный бот предназначен для просмотра расписания в колледже 'Галактика' "
                         "Чтобы воспользоваться ботом, нужно отправить команду !!! /schedule !!! "
                         "или выбрать ее в меню в левом нижнем углу")


@router.message(Command('help'))
async def command_help(message: Message) -> None:
    await message.answer("Чтобы воспользоваться ботом, нужно отправить боту команду '/schedule' или "
                         "выбрать соответствующую команду в меню бота в левом нижнем углу")


@router.message(Command('schedule'))
async def command_schedule(message: Message) -> None:
    keyboard_for_groups = create_keyboard_for_study_type()
    await message.answer("~~~ Просмотр расписания ~~~", reply_markup=keyboard_for_groups)
