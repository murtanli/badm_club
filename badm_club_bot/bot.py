import asyncio
import logging

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties

from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from utils.config import BOT_TOKEN, REDIS_URL
from core.logger import setup_logging
from handlers import router as main_router
from utils.reminder import daily_reminder_loop


async def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    dp = Dispatcher()

    dp.include_router(main_router)
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    asyncio.create_task(daily_reminder_loop(bot))

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Бот упал с ошибкой: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())