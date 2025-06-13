import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router
from config import BOT_TOKEN, WEBHOOK_URL

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

async def on_startup(dispatcher: Dispatcher, bot: Bot):
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook", drop_pending_updates=True)
    logging.info("✅ Webhook установлен!")

async def on_shutdown(dispatcher: Dispatcher, bot: Bot):
    await bot.delete_webhook()
    await bot.session.close()
    logging.info("🛑 Webhook удалён!")

async def handle_webhook(request):
    data = await request.json()
    update = bot.session._client._build_update(data)
    await dp.feed_update(bot, update)
    return web.Response()

async def create_app():
    app = web.Application()
    app["bot"] = bot
    app["dp"] = dp
    app.router.add_post("/webhook", handle_webhook)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    return app

if __name__ == "__main__":
    app = asyncio.run(create_app())
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)
