import logging
import os
from aiohttp import web # Добавляем импорт web из aiohttp

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from handlers import router # Импортируем роутер из handlers
from config import BOT_TOKEN, WEBHOOK_URL # Импортируем BOT_TOKEN и WEBHOOK_URL из config

# Настройка логов
logging.basicConfig(level=logging.INFO)

# Инициализация бота с дефолтными настройками
# Используем DefaultBotProperties для установки ParseMode по умолчанию
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2))
# Инициализация диспетчера с хранилищем в памяти
dp = Dispatcher(storage=MemoryStorage())

# Регистрация роутера (всех обработчиков)
# Все обработчики из handlers.py будут включены в диспетчер
dp.include_router(router)

async def on_startup(dispatcher: Dispatcher, bot: Bot):
    # Функция, которая выполняется при запуске веб-приложения
    # Устанавливаем вебхук для бота, чтобы Telegram знал, куда отправлять обновления
    # drop_pending_updates=True гарантирует, что бот начнет получать обновления с чистого листа
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook", drop_pending_updates=True)
    logging.info("Webhook установлен!")

async def on_shutdown(dispatcher: Dispatcher, bot: Bot):
    # Функция, которая выполняется при завершении работы веб-приложения
    # Удаляем вебхук, чтобы избежать отправки обновлений на неработающий сервер
    await bot.delete_webhook()
    logging.info("Webhook удален.")
    # Закрываем сессию бота
    await bot.session.close()

def main():
    # Создаем экземпляр AIOHTTP веб-приложения
    app = web.Application()
    # Сохраняем объекты бота и диспетчера в приложении aiohttp
    # Это позволяет получить к ним доступ в обработчиках веб-запросов
    app["bot"] = bot
    app["dp"] = dp

    # Настраиваем маршрут POST-запросов на '/webhook'
    # Все входящие POST-запросы на этот URL будут переданы в dp.web_hook_update
    # aiogram обработает их как обновления от Telegram
    app.router.add_post("/webhook", dp.web_hook_update)

    # Регистрируем функции on_startup и on_shutdown для диспетчера
    # Они будут вызваны aiogram при соответствующем событии
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Получаем номер порта из переменной окружения 'PORT'
    # Google Cloud Run автоматически устанавливает эту переменную.
    # Если переменная не установлена (например, при локальном запуске), используется 8080.
    port = int(os.environ.get("PORT", 8080))

    # Запускаем веб-сервер AIOHTTP
    # host="0.0.0.0" позволяет серверу слушать на всех доступных сетевых интерфейсах,
    # что необходимо в контейнерных средах.
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()