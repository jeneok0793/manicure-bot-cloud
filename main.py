from aiohttp import web

async def handle(request):
    return web.Response(text="✅ Bot is alive! Cloud Run is working.")

app = web.Application()
app.add_routes([web.get("/", handle)])

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, port=port)
