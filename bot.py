import asyncio
from random import randint
from typing import Any, Callable, Dict, Awaitable
from datetime import datetime
from aiogram import BaseMiddleware, Dispatcher, Router, Bot
from aiogram.types import TelegramObject, Message
from aiogram.filters import Command

API_TOKEN = "8096079559:AAFg_Yn4P4RA0RdYw4B9GQJuvdLpZoFi84s"

router = Router()
dp = Dispatcher()


# Middleware for generating internal user ID
class UserInternalMiddleware(BaseMiddleware):
    def get_internal_user_id(self, user_id: int):
        return randint(100_000_000, 900_000_000) + user_id

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user = data["event_from_user"]
        data["internal_id"] = self.get_internal_user_id(user.id)
        return await handler(event, data)


# Middleware for checking "Happy Month"
class HappyMonthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        internal_id: int = data["internal_id"]
        current_month: int = datetime.now().month
        is_happy_month: bool = (internal_id % 12) == current_month
        data["is_happy_month"] = is_happy_month
        return await handler(event, data)
    

# Command handler for the /happymonth command
@router.message(Command("happymonth"))
async def cmd_happymonth(
        message: Message,
        internal_id: int,
        is_happy_month: bool
):
    phrases = [f"Ваш ID в нашем сервисе: {internal_id}"]
    if is_happy_month:
        phrases.append("Сейчас ваш счастливый месяц!")
    else:
        phrases.append("В этом месяце будьте осторожнее...")
    await message.answer(". ".join(phrases))


# Main function to set up bot
async def main():
    bot = Bot(token=API_TOKEN)

    # Register middlewares
    dp.update.middleware(UserInternalMiddleware())  # Middleware that modifies updates globally
    router.message.middleware(HappyMonthMiddleware())  # Middleware for messages in router

    # Include router into dispatcher
    dp.include_router(router)

    # Start polling
    await dp.start_polling(bot)


# Entry point of the script
if __name__ == "__main__":
    print("Bot started")
    asyncio.run(main())
