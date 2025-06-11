import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web
from config import BOT_TOKEN, WEBHOOK_URL
from handlers import router

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(router)

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    await bot.delete_webhook()

async def handle_request(request):
    body = await request.read()
    await dp.feed_webhook_update(bot=bot, update=body, headers=request.headers)
    return web.Response()

def create_app():
    app = web.Application()
    app.router.add_post("/webhook", handle_request)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    port = int(os.environ.get("PORT", "8080"))  # ПОРТ ОБЯЗАТЕЛЕН
    web.run_app(create_app(), host="0.0.0.0", port=port)
