import asyncio
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from src.telegram_bot.utils.utils import update_complete


class DBUpdateMiddlewareCallbackQuery(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        if not update_complete.is_set():
            await event.answer('Расписание в процессе обновления. Пожалуйста, ожидайте', show_alert=True)
            return
        else:
            await handler(event, data)


class DBUpdateMiddlewareMessage(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if not update_complete.is_set():
            msg = await event.reply('Расписание в процессе обновления. Пожалуйста, ожидайте')
            await asyncio.sleep(2)
            await event.delete()
            await msg.delete()
            return
        else:
            await handler(event, data)
