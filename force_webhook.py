import asyncio
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN, WEBHOOK_URL  # ✅ импорт из config

async def set_webhook():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2))
    await bot.set_webhook(WEBHOOK_URL + "/webhook", drop_pending_updates=True)
    print("Webhook установлен!")

asyncio.run(set_webhook())
