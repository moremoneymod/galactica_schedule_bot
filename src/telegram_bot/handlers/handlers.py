from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

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
    builder = InlineKeyboardBuilder()
    builder.button(text="Очная форма обучения", callback_data="full_time")
    builder.button(text="Заочная форма обучения", callback_data="part_time")
    builder.adjust(1, 1)
    await message.answer("~~~ Просмотр расписания ~~~", reply_markup=builder.as_markup())
