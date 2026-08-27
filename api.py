"""aiohttp routes backing the Telegram Mini App (webapp_page.py).
Every request must carry a valid Telegram WebApp initData string, checked
against the bot token per security.validate_init_data.
"""

import json

from aiohttp import web

import db
from security import validate_init_data
from webapp_page import get_webapp_html


def _auth(request: web.Request):
    init_data = request.headers.get("X-Telegram-Init-Data", "")
    data = validate_init_data(init_data)
    if not data or "user" not in data:
        return None
    return data["user"]["id"]


async def webapp_page(request: web.Request):
    return web.Response(text=get_webapp_html(), content_type="text/html")


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


def register(app: web.Application, webapp_path: str):
    app.router.add_get(webapp_path, webapp_page)
    app.router.add_get("/api/tasks", list_tasks)
    app.router.add_post("/api/tasks", add_task)
    app.router.add_post("/api/tasks/{task_id}/toggle", toggle_task)
    app.router.add_delete("/api/tasks/{task_id}", delete_task)
