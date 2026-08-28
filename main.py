import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

import api
import db
from config import (
    BOT_TOKEN,
    RUN_MODE,
    WEBHOOK_URL,
    WEBHOOK_PATH,
    WEBAPP_PATH,
    PORT,
    PRICE_WATCH_ENABLED,
)
from handlers import router
from inline_handlers import router as inline_router
from watch_service import run_watch_loop

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("bot.main")


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    dp.include_router(inline_router)
    return dp


async def _on_startup_polling(bot: Bot):
    await db.init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    log.info("Polling mode: webhook removed, starting long polling.")


async def run_polling():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = build_dispatcher()
    await _on_startup_polling(bot)
    if PRICE_WATCH_ENABLED:
        asyncio.create_task(run_watch_loop(bot))
    await dp.start_polling(bot)


def run_webhook():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = build_dispatcher()

    async def on_startup(app: web.Application):
        await db.init_db()
        app["bot"] = bot  # so api.py's admin broadcast endpoint can reach it
        if WEBHOOK_URL:
            log.info("Webhook mode: attempting to set webhook to %s", WEBHOOK_URL)
            await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
            log.info("Webhook mode: webhook set successfully.")
        else:
            log.warning(
                "WEBHOOK_HOST is not set yet - webhook was NOT registered with Telegram. "
                "Set WEBHOOK_HOST to this service's public URL and redeploy."
            )
        if PRICE_WATCH_ENABLED:
            app["watch_task"] = asyncio.create_task(run_watch_loop(bot))

    async def on_cleanup(app: web.Application):
        watch_task = app.get("watch_task")
        if watch_task:
            watch_task.cancel()

    async def health(request):
        return web.Response(text="ok")

    app = web.Application()
    app.router.add_get("/", health)  # keeps Render/uptime pings happy
    api.register(app, WEBAPP_PATH)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    web.run_app(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    if RUN_MODE == "webhook":
        run_webhook()
    else:
        asyncio.run(run_polling())
