import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiohttp import web
from config import BOT_TOKEN, WEBHOOK_URL
from handlers import router

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)

async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL)
    logging.info("✅ Webhook set successfully")

async def handle(request):
    try:
        data = await request.json()
        update = Update.model_validate(data)
        await dp.feed_update(bot, update)
        return web.Response()
    except Exception as e:
        logging.error(f"❌ Error handling update: {e}")
        return web.Response(status=500)

app = web.Application()
app.router.add_post("/", handle)
app.on_startup.append(on_startup)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    web.run_app(app, port=8080)
