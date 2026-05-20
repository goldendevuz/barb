import asyncio
import logging
import os
import sys

# Loyiha ildizini PYTHONPATH ga qo'shish (Docker va lokal uchun)
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
os.chdir(_ROOT)

import core.envs  # noqa: E402, F401 — .env yuklash

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from core.envs import TELEGRAM_BOT_TOKEN
from integrations.telegram.handlers import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


async def main():
    token = TELEGRAM_BOT_TOKEN
    if not token:
        summary = core.envs.env_debug_summary()
        logger.error("TELEGRAM_BOT_TOKEN topilmadi. Env holati: %s", summary)
        sys.exit(1)

    logger.info("Starting Aiogram Telegram Bot...")

    bot = Bot(token=token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical("Bot crashed: %s", e)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
