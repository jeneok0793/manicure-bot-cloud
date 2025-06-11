import logging
import os
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from handlers import router
from config import BOT_TOKEN, WEBHOOK_URL

# Настройка логов
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

# Функции старта и остановки
async def on_startup(app: web.Application):
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook", drop_pending_updates=True)
    logging.info("Webhook установлен")

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()
    await bot.session.close()
    logging.info("Webhook удалён и сессия закрыта")

# Обработка запросов от Telegram
async def handle_webhook(request):
    update = await request.json()
    await dp.feed_raw_update(bot, update)
    return web.Response()

def main():
    app = web.Application()

    # Роутинг вебхука
    app.router.add_post("/webhook", handle_webhook)

    # Подключение lifecycle-хендлеров
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # Запуск приложения
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
