import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

from handlers import router
from config import BOT_TOKEN, WEBHOOK_URL

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

async def on_startup(dispatcher: Dispatcher, bot: Bot):
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook", drop_pending_updates=True)
    logging.info("✅ Webhook установлен")

async def on_shutdown(dispatcher: Dispatcher, bot: Bot):
    await bot.delete_webhook()
    await bot.session.close()
    logging.info("🛑 Webhook удалён")

def main():
    app = web.Application()
    app["bot"] = bot
    app["dp"] = dp

    # Подключение webhook обработчика
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")

    # Регистрация событий запуска и завершения
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Получение порта
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()