"""aiohttp routes backing the Telegram Mini App (webapp_page.py).
Every request must carry a valid Telegram WebApp initData string, checked
against the bot token per security.validate_init_data.
"""

import asyncio
import json
import logging

import aiohttp
from aiohttp import web

import db
from security import validate_init_data
from webapp_page import get_webapp_html
from handlers import _geocode_city, _fetch_weather, _uah_rate, LANG_TO_GEOCODE
from i18n import weather_desc
from config import ADMIN_ID

log = logging.getLogger("bot.api")


def _auth(request: web.Request):
    init_data = request.headers.get("X-Telegram-Init-Data", "")
    data = validate_init_data(init_data)
    if not data or "user" not in data:
        return None
    return data["user"]["id"]


def _require_admin(request: web.Request):
    """Returns the caller's user id if they're authenticated AND match
    ADMIN_ID, otherwise None. Used to gate every /api/admin/* route."""
    user_id = _auth(request)
    if user_id is None or not ADMIN_ID or user_id != ADMIN_ID:
        return None
    return user_id


async def webapp_page(request: web.Request):
    return web.Response(text=get_webapp_html(), content_type="text/html")


async def me(request: web.Request):
    """Tells the Mini App whether to show the Admin tab. Not itself a source
    of admin data - every actual admin route re-checks ADMIN_ID on its own."""
    user_id = _auth(request)
    if user_id is None:
        return web.json_response({"error": "unauthorized"}, status=401)
    return web.json_response({"is_admin": bool(ADMIN_ID) and user_id == ADMIN_ID})


async def list_tasks(request: web.Request):
    user_id = _auth(request)
    if user_id is None:
        return web.json_response({"error": "unauthorized"}, status=401)
    await db.ensure_user(user_id)
    tasks = await db.list_tasks(user_id, include_done=True)
    return web.json_response(
        {"tasks": [{"id": t_id, "text": text, "done": bool(done)} for t_id, text, done in tasks]}
    )


async def add_task(request: web.Request):
    user_id = _auth(request)
    if user_id is None:
        return web.json_response({"error": "unauthorized"}, status=401)
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return web.json_response({"error": "invalid body"}, status=400)
    text = (body.get("text") or "").strip()[:200]
    if not text:
        return web.json_response({"error": "text required"}, status=400)
    await db.ensure_user(user_id)
    task_id = await db.add_task(user_id, text)
    return web.json_response({"id": task_id})


async def toggle_task(request: web.Request):
    user_id = _auth(request)
    if user_id is None:
        return web.json_response({"error": "unauthorized"}, status=401)
    task_id = int(request.match_info["task_id"])
    await db.complete_task(user_id, task_id)
    return web.json_response({"ok": True})


async def delete_task(request: web.Request):
    user_id = _auth(request)
    if user_id is None:
        return web.json_response({"error": "unauthorized"}, status=401)
    task_id = int(request.match_info["task_id"])
    await db.delete_task(user_id, task_id)
    return web.json_response({"ok": True})


async def get_weather(request: web.Request):
    user_id = _auth(request)
    if user_id is None:
        return web.json_response({"error": "unauthorized"}, status=401)
    city = (request.query.get("city") or "").strip()
    if not city:
        return web.json_response({"error": "city required"}, status=400)
    lang = await db.get_lang(user_id)
    try:
        async with aiohttp.ClientSession() as session:
            place = await _geocode_city(session, city, preferred=LANG_TO_GEOCODE.get(lang, "en"))
            if not place:
                return web.json_response({"error": "not_found"}, status=404)
            current = await _fetch_weather(session, place["latitude"], place["longitude"])
        if not current:
            return web.json_response({"error": "not_found"}, status=404)
        country = place.get("country_code", "")
        label = f"{place.get('name', city)}, {country}" if country else place.get("name", city)
        return web.json_response(
            {
                "city": label,
                "temp": current.get("temperature"),
                "wind": current.get("windspeed"),
                "desc": weather_desc(current.get("weathercode", -1), lang),
            }
        )
    except Exception:
        log.exception("weather API call failed")
        return web.json_response({"error": "upstream_failed"}, status=502)


async def get_currency(request: web.Request):
    user_id = _auth(request)
    if user_id is None:
        return web.json_response({"error": "unauthorized"}, status=401)
    try:
        async with aiohttp.ClientSession() as session:
            usd, eur = await asyncio.gather(_uah_rate(session, "USD"), _uah_rate(session, "EUR"))
        if usd is None or eur is None:
            raise ValueError("missing rate")
        return web.json_response({"usd": usd, "eur": eur})
    except Exception:
        log.exception("currency API call failed")
        return web.json_response({"error": "upstream_failed"}, status=502)


async def admin_stats(request: web.Request):
    if _require_admin(request) is None:
        return web.json_response({"error": "forbidden"}, status=403)
    return web.json_response(await db.get_stats())


async def admin_broadcast(request: web.Request):
    if _require_admin(request) is None:
        return web.json_response({"error": "forbidden"}, status=403)
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return web.json_response({"error": "invalid body"}, status=400)
    text = (body.get("text") or "").strip()[:4000]
    if not text:
        return web.json_response({"error": "text required"}, status=400)

    bot = request.app.get("bot")
    if bot is None:
        return web.json_response({"error": "bot unavailable"}, status=503)

    user_ids = await db.all_user_ids()
    sent = 0
    for uid in user_ids:
        try:
            await bot.send_message(uid, text)
            sent += 1
        except Exception:
            log.warning("admin broadcast failed for %s", uid)
        await asyncio.sleep(0.05)  # stay well under Telegram's rate limits
    return web.json_response({"sent": sent, "total": len(user_ids)})


def register(app: web.Application, webapp_path: str):
    app.router.add_get(webapp_path, webapp_page)
    app.router.add_get("/api/me", me)
    app.router.add_get("/api/tasks", list_tasks)
    app.router.add_post("/api/tasks", add_task)
    app.router.add_post("/api/tasks/{task_id}/toggle", toggle_task)
    app.router.add_delete("/api/tasks/{task_id}", delete_task)
    app.router.add_get("/api/weather", get_weather)
    app.router.add_get("/api/currency", get_currency)
    app.router.add_get("/api/admin/stats", admin_stats)
    app.router.add_post("/api/admin/broadcast", admin_broadcast)
