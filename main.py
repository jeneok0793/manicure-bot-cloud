from aiohttp import web

async def handler(request):
    return web.Response(text="✅ Бот работает")

app = web.Application()
app.router.add_get("/", handler)

if __name__ == "__main__":
    web.run_app(app, port=8080)
