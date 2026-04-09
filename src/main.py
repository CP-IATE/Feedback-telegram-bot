import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import config as cfg
import dataBase as db
from handlers import admin, client
from middleware import ThrottlingMiddleware #,BlacklistMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    db.create_db()
    logger.info("База даних ініціалізована")

    bot = Bot(
        token=cfg.TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Middleware (порядок важливий спочатку blacklist потім throttling)
    #dp.message.middleware(BlacklistMiddleware())
    dp.message.middleware(ThrottlingMiddleware(rate_limit=1.5))

    # Роутери
    dp.include_router(admin.router)
    dp.include_router(client.router)

    logger.info("Бот запускається...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Бот зупинений")

if __name__ == "__main__":
    asyncio.run(main())
