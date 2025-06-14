import asyncio
from aiogram import Bot
from config import BOT_TOKEN, WEBHOOK_URL

async def set_webhook():
    bot = Bot(token=BOT_TOKEN)
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook", drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(set_webhook())
