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
# from middlewares.admin_check import AdminCheckMiddleware
# from middlewares.Scheduling_ispatcher_check import SchedulingDispatcherCheckMiddleware

async def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    # storage = RedisStorage.from_url(REDIS_URL)
    dp = Dispatcher()

    # admin_middleware = AdminCheckMiddleware()
    # schedule_dispatcher_middleware = SchedulingDispatcherCheckMiddleware()

    # #connect admin middleware
    # dp.update.middleware(admin_middleware)
    # dp.message.middleware(admin_middleware)
    # dp.callback_query.middleware(admin_middleware)
    #
    # # connect schedule dispatcher middleware
    # dp.update.middleware(schedule_dispatcher_middleware)
    # dp.message.middleware(schedule_dispatcher_middleware)
    # dp.callback_query.middleware(schedule_dispatcher_middleware)

    dp.include_router(main_router)
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Бот упал с ошибкой: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())