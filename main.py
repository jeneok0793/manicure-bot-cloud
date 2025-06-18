import logging
import os
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from handlers import router
from config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

# Запускается при старте контейнера
async def on_startup(dispatcher: Dispatcher, bot: Bot):
    logging.info("🚀 Бот запущен!")

# Вызывается при остановке контейнера
async def on_shutdown(dispatcher: Dispatcher, bot: Bot):
    await bot.session.close()
    logging.info("🛑 Бот остановлен.")

def main():
    app = web.Application()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Регистрируем обработчик вебхука
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
    setup_application(app, dp, bot=bot)

    # Cloud Run требует порт 8080
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
