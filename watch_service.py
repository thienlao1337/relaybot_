"""Background job: polls exchange rates and fires one-shot user alerts.

This is the "real-time monitoring + instant notification" pattern - watch an
external source, notify the moment a condition is met - kept small enough to
run as a plain asyncio task on the bot's own event loop instead of a separate
worker process or task queue. It runs identically in polling and webhook mode;
see main.py for where it's started.
"""

import asyncio
import logging

import aiohttp
from aiogram import Bot

import db
from handlers import _uah_rate
from i18n import t

log = logging.getLogger("bot.watch")

POLL_INTERVAL_SECONDS = 300  # 5 minutes - gentle on the free open.er-api.com API


async def _check_once(bot: Bot):
    watchers = await db.list_active_watchers()
    if not watchers:
        return

    async with aiohttp.ClientSession() as session:
        usd, eur = await asyncio.gather(_uah_rate(session, "USD"), _uah_rate(session, "EUR"))
    rates = {"USD": usd, "EUR": eur}

    for watcher in watchers:
        rate = rates.get(watcher.currency)
        if rate is None:
            continue
        triggered = (watcher.direction == "above" and rate >= watcher.threshold) or (
            watcher.direction == "below" and rate <= watcher.threshold
        )
        if not triggered:
            continue
        lang = await db.get_lang(watcher.user_id)
        try:
            await bot.send_message(
                watcher.user_id,
                t(
                    "watch_triggered",
                    lang,
                    currency=watcher.currency,
                    rate=round(rate, 2),
                    threshold=watcher.threshold,
                ),
            )
        except Exception:
            log.warning("watch notification failed for user %s", watcher.user_id)
        await db.deactivate_watcher(watcher.id)


async def run_watch_loop(bot: Bot):
    log.info("Price watch loop started (interval=%ss).", POLL_INTERVAL_SECONDS)
    while True:
        try:
            await _check_once(bot)
        except Exception:
            log.exception("price watch iteration failed")
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
