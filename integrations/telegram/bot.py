import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from core.envs import TELEGRAM_BOT_TOKEN

# Add the parent parent path so that integrations can be loaded if run standalone
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from integrations.telegram.handlers import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def main():
    token = TELEGRAM_BOT_TOKEN
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN is not defined in environment variables.")
        sys.exit(1)
        
    logger.info("🤖 Starting Aiogram Telegram Bot...")
    
    # Initialize bot and dispatcher
    bot = Bot(token=token)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register router handlers
    dp.include_router(router)
    
    # Delete webhook to prevent conflicts with other sessions
    await bot.delete_webhook(drop_pending_updates=True)
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"💥 Bot crashed: {str(e)}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🤖 Bot stopped.")
