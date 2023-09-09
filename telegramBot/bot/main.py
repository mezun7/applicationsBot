import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from applicationsBot import settings
from applicationsBot.settings import TGBOT_MEMORY

dp = None
bot = None


async def main():
    from telegramBot.bot.parents_handler import parents_router
    from telegramBot.bot.handlers import router
    global dp, bot
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=TGBOT_MEMORY)
    dp.include_routers(router, parents_router)
    # dp.include_router(parents_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    # await dp.storage.close()

