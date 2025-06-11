import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config import BOT_TOKEN, WEBHOOK_URL
from handlers import router

logging.basicConfig(level=logging.INFO)

# Создание бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

# Webhook URL
WEBHOOK_PATH = "/webhook"
WEBHOOK_FULL_URL = WEBHOOK_URL + WEBHOOK_PATH

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_FULL_URL, drop_pending_updates=True)
    logging.info("Webhook установлен")

async def on_shutdown(app):
    await bot.delete_webhook()
    logging.info("Webhook удалён")

def main():
    app = web.Application()

    # Привязываем aiogram к AIOHTTP
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # Получаем порт из переменной окружения (Cloud Run использует PORT=8080)
    port = int(os.getenv("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
