import asyncio
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN  # ✅ импорт из config

async def check_webhook():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2))
    info = await bot.get_webhook_info()
    print("Webhook info:", info.url)

asyncio.run(check_webhook())
