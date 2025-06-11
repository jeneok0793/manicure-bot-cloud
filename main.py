from aiogram import Bot, Dispatcher
from aiogram.web import App
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import register_handlers
import logging

# Настройка логов
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Регистрируем обработчики
register_handlers(dp)

# Создаём web-приложение
app = App(dispatcher=dp, bot=bot)
