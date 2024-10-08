import asyncio
import logging
import sys

from datetime import datetime
from typing import  Any, Callable, Dict, Awaitable
from urllib.request import build_opener

from aiogram import  Bot, Dispatcher, Router, BaseMiddleware, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardBuilder

router = Router()

class WeekendCallbackMiddleware(BaseMiddleware):
    def is_weekend(self) -> bool:
        return datetime.utcnow().weekday() in (5,6)
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str,Any]], Awaitable[None]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any :
        if not isinstance(event, CallbackQuery):
            return await handler(event, data)
        if not self.is_weekend():
            return await handler(event, data)
        await event.answer(
            "Какая работа? Завод остановлен до понедельника!",
            show_alert=True
        )
@router.message(Command("checkin"))
async def cmd_checkin(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="Я на работе!", callback_data="checkin")
    await message.answer(
        text = "Нажимайте эту кнопку только по будним дням!",
        reply_markup = builder.as_markup()
    )

@router.callback_query(F.data == "checkin")
async def cmd_checkin(callback : CallbackQuery):
    await callback.answer(
        text="Спасибо, что подтвердили своё присутствие!",
        show_alert=True
    )

async def main() -> None :
    bot = Bot('8096079559:AAFg_Yn4P4RA0RdYw4B9GQJuvdLpZoFi84s')
    dp = Dispatcher()
    dp.callback_query.outer_middleware(WeekendCallbackMiddleware())
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())