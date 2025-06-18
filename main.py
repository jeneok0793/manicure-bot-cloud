from aiohttp import web
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers_google import router as google_router

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(google_router)

async def handle(request):
    body = await request.read()
    headers = request.headers
    await dp.feed_webhook_update(bot=bot, update=body, headers=headers)
    return web.Response()

async def on_startup(app):
    await bot.set_webhook("https://manicure-bot-cloud-xxxxx.a.run.app/webhook")  # вставь свой URL

app = web.Application()
app.router.add_post("/webhook", handle)
app.on_startup.append(on_startup)

if __name__ == "__main__":
    web.run_app(app, port=8080)
