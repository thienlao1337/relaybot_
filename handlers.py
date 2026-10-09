import asyncio
import logging
import time

import aiohttp
from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
    LabeledPrice,
    PreCheckoutQuery,
)

import db
import knowledge_base
import llm
from i18n import t, weather_desc, lang_from_telegram
from config import ADMIN_ID, AI_ENABLED, AI_COOLDOWN_SECONDS, WEBAPP_URL, STARS_PRICE

router = Router()
log = logging.getLogger("bot.handlers")

_ai_last_call: dict[int, float] = {}  # user_id -> unix timestamp of last AI request


# ---------- FSM states ----------
class TaskForm(StatesGroup):
    waiting_text = State()


class WeatherForm(StatesGroup):
    waiting_city = State()


class AIForm(StatesGroup):
    waiting_question = State()


class WatchForm(StatesGroup):
    waiting_threshold = State()


# ---------- keyboards ----------
def main_menu_kb(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=t("menu_tasks", lang), callback_data="menu:tasks")],
        [InlineKeyboardButton(text=t("menu_weather", lang), callback_data="menu:weather")],
        [InlineKeyboardButton(text=t("menu_currency", lang), callback_data="menu:currency")],
        [InlineKeyboardButton(text=t("menu_watch", lang), callback_data="menu:watch")],
        [InlineKeyboardButton(text=t("menu_ai", lang), callback_data="menu:ai")],
    ]
    if WEBAPP_URL:
        rows.append(
            [InlineKeyboardButton(text=t("menu_webapp", lang), web_app=WebAppInfo(url=WEBAPP_URL))]
        )
    else:
        rows.append([InlineKeyboardButton(text=t("menu_webapp", lang), callback_data="menu:webapp_unavailable")])
    rows.append([InlineKeyboardButton(text=t("menu_stars", lang), callback_data="menu:stars")])
    rows.append(
        [
            InlineKeyboardButton(text=t("menu_lang", lang), callback_data="menu:lang"),
            InlineKeyboardButton(text=t("menu_help", lang), callback_data="menu:help"),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def back_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t("back", lang), callback_data="menu:back")]]
    )


def tasks_kb(lang: str, tasks) -> InlineKeyboardMarkup:
    rows = []
    for task_id, text_, done in tasks:
        label = f"✅ {text_}" if done else text_
        rows.append(
            [
                InlineKeyboardButton(text=label[:40], callback_data="noop"),
                InlineKeyboardButton(text="✔️", callback_data=f"task:done:{task_id}"),
                InlineKeyboardButton(text="🗑", callback_data=f"task:del:{task_id}"),
            ]
        )
    rows.append([InlineKeyboardButton(text=t("tasks_add_btn", lang), callback_data="task:add")])
    rows.append([InlineKeyboardButton(text=t("back", lang), callback_data="menu:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def watch_list_kb(lang: str, watchers) -> InlineKeyboardMarkup:
    rows = []
    for watcher_id, currency, direction, threshold in watchers:
        dir_word = t(f"watch_direction_word_{direction}", lang)
        label = f"{currency} {dir_word} {threshold}"
        rows.append(
            [
                InlineKeyboardButton(text=label[:40], callback_data="noop"),
                InlineKeyboardButton(text="🗑", callback_data=f"watch:del:{watcher_id}"),
            ]
        )
    rows.append([InlineKeyboardButton(text=t("watch_add_btn", lang), callback_data="watch:add")])
    rows.append([InlineKeyboardButton(text=t("back", lang), callback_data="menu:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def watch_currency_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="USD", callback_data="watch:cur:USD"),
                InlineKeyboardButton(text="EUR", callback_data="watch:cur:EUR"),
            ]
        ]
    )


def watch_direction_kb(lang: str, currency: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("watch_dir_above", lang), callback_data=f"watch:dir:{currency}:above")],
            [InlineKeyboardButton(text=t("watch_dir_below", lang), callback_data=f"watch:dir:{currency}:below")],
        ]
    )


def lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Українська", callback_data="lang:ua"),
                InlineKeyboardButton(text="English", callback_data="lang:en"),
                InlineKeyboardButton(text="Русский", callback_data="lang:ru"),
            ]
        ]
    )


# ---------- /start ----------
@router.message(CommandStart())
async def cmd_start(message: Message):
    lang = await db.ensure_user(
        message.from_user.id, default_lang=lang_from_telegram(message.from_user.language_code)
    )
    await message.answer(
        t("welcome", lang, name=message.from_user.first_name or "there"),
        reply_markup=main_menu_kb(lang),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    lang = await db.get_lang(message.from_user.id)
    await message.answer(t("help", lang))


# ---------- menu navigation ----------
@router.callback_query(F.data == "menu:back")
async def cb_back(call: CallbackQuery):
    lang = await db.get_lang(call.from_user.id)
    await call.message.edit_text(
        t("welcome", lang, name=call.from_user.first_name or "there"),
        reply_markup=main_menu_kb(lang),
    )
    await call.answer()


@router.callback_query(F.data == "menu:help")
async def cb_help(call: CallbackQuery):
    lang = await db.get_lang(call.from_user.id)
    await call.message.edit_text(t("help", lang), reply_markup=back_kb(lang))
    await call.answer()


@router.callback_query(F.data == "noop")
async def cb_noop(call: CallbackQuery):
    await call.answer()


# ---------- tasks ----------
@router.callback_query(F.data == "menu:tasks")
async def cb_tasks(call: CallbackQuery):
    lang = await db.get_lang(call.from_user.id)
    tasks = await db.list_tasks(call.from_user.id)
    text = t("tasks_empty", lang) if not tasks else t("tasks_title", lang)
    await call.message.edit_text(text, reply_markup=tasks_kb(lang, tasks))
    await call.answer()


@router.callback_query(F.data == "task:add")
async def cb_task_add(call: CallbackQuery, state: FSMContext):
    lang = await db.get_lang(call.from_user.id)
    await call.message.edit_text(t("tasks_ask", lang), reply_markup=back_kb(lang))
    await state.set_state(TaskForm.waiting_text)
    await call.answer()


@router.message(TaskForm.waiting_text, F.text & ~F.text.startswith("/"))
async def task_text_received(message: Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    await db.add_task(message.from_user.id, message.text.strip()[:200])
    await state.clear()
    tasks = await db.list_tasks(message.from_user.id)
    await message.answer(t("tasks_added", lang), reply_markup=tasks_kb(lang, tasks))


@router.callback_query(F.data.startswith("task:done:"))
async def cb_task_done(call: CallbackQuery):
    lang = await db.get_lang(call.from_user.id)
    task_id = int(call.data.split(":")[2])
    await db.complete_task(call.from_user.id, task_id)
    tasks = await db.list_tasks(call.from_user.id)
    text = t("tasks_empty", lang) if not tasks else t("tasks_title", lang)
    await call.message.edit_text(text, reply_markup=tasks_kb(lang, tasks))
    await call.answer(t("tasks_done", lang))


@router.callback_query(F.data.startswith("task:del:"))
async def cb_task_del(call: CallbackQuery):
    lang = await db.get_lang(call.from_user.id)
    task_id = int(call.data.split(":")[2])
    await db.delete_task(call.from_user.id, task_id)
    tasks = await db.list_tasks(call.from_user.id)
    text = t("tasks_empty", lang) if not tasks else t("tasks_title", lang)
    await call.message.edit_text(text, reply_markup=tasks_kb(lang, tasks))
    await call.answer()


@router.message(Command("tasks"))
async def cmd_tasks(message: Message):
    lang = await db.get_lang(message.from_user.id)
    tasks = await db.list_tasks(message.from_user.id)
    text = t("tasks_empty", lang) if not tasks else t("tasks_title", lang)
    await message.answer(text, reply_markup=tasks_kb(lang, tasks))


# ---------- weather (open-meteo, no API key required) ----------
# Open-Meteo's geocoder only matches a name against its index for the *given*
# language - a Cyrillic query like "Київ" returns nothing under language=en, but
# matches fine under language=uk. So we try a short chain of languages, starting
# with whichever matches the user's bot language, and stop at the first hit.
LANG_TO_GEOCODE = {"ua": "uk", "en": "en", "ru": "ru"}


async def _geocode_city(session: aiohttp.ClientSession, city: str, preferred: str = "en"):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    order = [preferred] + [code for code in ("en", "uk", "ru") if code != preferred]
    for code in order:
        async with session.get(url, params={"name": city, "count": 1, "language": code}) as resp:
            data = await resp.json()
            results = data.get("results") or []
            if results:
                return results[0]
    return None


async def _fetch_weather(session: aiohttp.ClientSession, lat: float, lon: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": lat, "longitude": lon, "current_weather": "true"}
    async with session.get(url, params=params) as resp:
        data = await resp.json()
        return data.get("current_weather")


@router.callback_query(F.data == "menu:weather")
async def cb_weather(call: CallbackQuery, state: FSMContext):
    lang = await db.get_lang(call.from_user.id)
    await call.message.edit_text(t("weather_ask", lang), reply_markup=back_kb(lang))
    await state.set_state(WeatherForm.waiting_city)
    await call.answer()


@router.message(Command("weather"))
async def cmd_weather(message: Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    await message.answer(t("weather_ask", lang))
    await state.set_state(WeatherForm.waiting_city)


@router.message(WeatherForm.waiting_city, F.text & ~F.text.startswith("/"))
async def weather_city_received(message: Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    city = message.text.strip()
    async with aiohttp.ClientSession() as session:
        place = await _geocode_city(session, city, preferred=LANG_TO_GEOCODE.get(lang, "en"))
        if not place:
            await message.answer(t("weather_not_found", lang))
            return
        current = await _fetch_weather(session, place["latitude"], place["longitude"])
    await state.clear()
    if not current:
        await message.answer(t("weather_not_found", lang))
        return
    label = place.get("name", city)
    country = place.get("country_code", "")
    full_label = f"{label}, {country}" if country else label
    await message.answer(
        t(
            "weather_result",
            lang,
            city=full_label,
            temp=current.get("temperature"),
            wind=current.get("windspeed"),
            desc=weather_desc(current.get("weathercode", -1), lang),
        ),
        reply_markup=back_kb(lang),
    )


# ---------- currency (open.er-api.com, no API key required) ----------
async def _uah_rate(session: aiohttp.ClientSession, base: str) -> float | None:
    url = f"https://open.er-api.com/v6/latest/{base}"
    async with session.get(url) as resp:
        data = await resp.json()
        rates = data.get("rates") or {}
        return rates.get("UAH")


@router.callback_query(F.data == "menu:currency")
async def cb_currency(call: CallbackQuery):
    lang = await db.get_lang(call.from_user.id)
    await call.message.edit_text(t("currency_loading", lang))
    try:
        async with aiohttp.ClientSession() as session:
            usd, eur = await asyncio.gather(
                _uah_rate(session, "USD"), _uah_rate(session, "EUR")
            )
        if usd is None or eur is None:
            raise ValueError("missing rate")
        await call.message.edit_text(
            t("currency_result", lang, usd=usd, eur=eur), reply_markup=back_kb(lang)
        )
    except Exception:
        log.exception("currency fetch failed")
        await call.message.edit_text(t("currency_error", lang), reply_markup=back_kb(lang))
    await call.answer()


@router.message(Command("currency"))
async def cmd_currency(message: Message):
    lang = await db.get_lang(message.from_user.id)
    msg = await message.answer(t("currency_loading", lang))
    try:
        async with aiohttp.ClientSession() as session:
            usd, eur = await asyncio.gather(
                _uah_rate(session, "USD"), _uah_rate(session, "EUR")
            )
        if usd is None or eur is None:
            raise ValueError("missing rate")
        await msg.edit_text(t("currency_result", lang, usd=usd, eur=eur))
    except Exception:
        log.exception("currency fetch failed")
        await msg.edit_text(t("currency_error", lang))


# ---------- currency rate alerts (background watcher demo) ----------
@router.callback_query(F.data == "menu:watch")
async def cb_watch(call: CallbackQuery):
    lang = await db.get_lang(call.from_user.id)
    watchers = await db.list_user_watchers(call.from_user.id)
    text = t("watch_list_empty", lang) if not watchers else t("watch_list_title", lang)
    await call.message.edit_text(text, reply_markup=watch_list_kb(lang, watchers))
    await call.answer()


@router.message(Command("watch"))
async def cmd_watch(message: Message):
    lang = await db.get_lang(message.from_user.id)
    watchers = await db.list_user_watchers(message.from_user.id)
    text = t("watch_list_empty", lang) if not watchers else t("watch_list_title", lang)
    await message.answer(text, reply_markup=watch_list_kb(lang, watchers))


@router.callback_query(F.data == "watch:add")
async def cb_watch_add(call: CallbackQuery):
    lang = await db.get_lang(call.from_user.id)
    await call.message.edit_text(t("watch_pick_currency", lang), reply_markup=watch_currency_kb())
    await call.answer()


@router.callback_query(F.data.startswith("watch:cur:"))
async def cb_watch_currency(call: CallbackQuery):
    lang = await db.get_lang(call.from_user.id)
    currency = call.data.split(":")[2]
    await call.message.edit_text(
        t("watch_pick_direction", lang, currency=currency), reply_markup=watch_direction_kb(lang, currency)
    )
    await call.answer()


@router.callback_query(F.data.startswith("watch:dir:"))
async def cb_watch_direction(call: CallbackQuery, state: FSMContext):
    lang = await db.get_lang(call.from_user.id)
    _, _, currency, direction = call.data.split(":")
    await state.update_data(currency=currency, direction=direction)
    await state.set_state(WatchForm.waiting_threshold)
    await call.message.edit_text(t("watch_ask_threshold", lang), reply_markup=back_kb(lang))
    await call.answer()


@router.message(WatchForm.waiting_threshold, F.text & ~F.text.startswith("/"))
async def watch_threshold_received(message: Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    raw = message.text.strip().replace(",", ".")
    try:
        threshold = float(raw)
    except ValueError:
        await message.answer(t("watch_invalid_number", lang))
        return
    data = await state.get_data()
    currency = data.get("currency", "USD")
    direction = data.get("direction", "above")
    await db.add_watcher(message.from_user.id, currency, direction, threshold)
    await state.clear()
    dir_word = t(f"watch_direction_word_{direction}", lang)
    await message.answer(t("watch_created", lang, currency=currency, direction=dir_word, threshold=threshold))
    watchers = await db.list_user_watchers(message.from_user.id)
    await message.answer(t("watch_list_title", lang), reply_markup=watch_list_kb(lang, watchers))


@router.callback_query(F.data.startswith("watch:del:"))
async def cb_watch_delete(call: CallbackQuery):
    lang = await db.get_lang(call.from_user.id)
    watcher_id = int(call.data.split(":")[2])
    await db.delete_watcher(call.from_user.id, watcher_id)
    watchers = await db.list_user_watchers(call.from_user.id)
    text = t("watch_list_empty", lang) if not watchers else t("watch_list_title", lang)
    await call.message.edit_text(text, reply_markup=watch_list_kb(lang, watchers))
    await call.answer(t("watch_deleted", lang))


# ---------- language ----------
@router.callback_query(F.data == "menu:lang")
async def cb_lang(call: CallbackQuery):
    lang = await db.get_lang(call.from_user.id)
    await call.message.edit_text(t("lang_pick", lang), reply_markup=lang_kb())
    await call.answer()


@router.message(Command("lang"))
async def cmd_lang(message: Message):
    lang = await db.get_lang(message.from_user.id)
    await message.answer(t("lang_pick", lang), reply_markup=lang_kb())


@router.callback_query(F.data.startswith("lang:"))
async def cb_lang_set(call: CallbackQuery):
    new_lang = call.data.split(":")[1]
    await db.set_lang(call.from_user.id, new_lang)
    await call.message.edit_text(t("lang_set", new_lang), reply_markup=main_menu_kb(new_lang))
    await call.answer()


# ---------- admin broadcast ----------
@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, bot: Bot):
    lang = await db.get_lang(message.from_user.id)
    if not ADMIN_ID or message.from_user.id != ADMIN_ID:
        await message.answer(t("broadcast_denied", lang))
        return
    text = message.text.partition(" ")[2].strip()
    if not text:
        await message.answer(t("broadcast_usage", lang))
        return
    user_ids = await db.all_user_ids()
    sent = 0
    for uid in user_ids:
        try:
            await bot.send_message(uid, text)
            sent += 1
        except Exception:
            log.warning("broadcast failed for %s", uid)
        await asyncio.sleep(0.05)  # stay well under Telegram's rate limits
    await message.answer(t("broadcast_done", lang, n=sent))


# ---------- mini app ----------
@router.callback_query(F.data == "menu:webapp_unavailable")
async def cb_webapp_unavailable(call: CallbackQuery):
    lang = await db.get_lang(call.from_user.id)
    await call.answer(t("webapp_unavailable", lang), show_alert=True)


# ---------- AI assistant ----------
@router.callback_query(F.data == "menu:ai")
async def cb_ai(call: CallbackQuery, state: FSMContext):
    lang = await db.get_lang(call.from_user.id)
    if not AI_ENABLED:
        await call.answer(t("ai_disabled", lang), show_alert=True)
        return
    await call.message.edit_text(t("ai_ask", lang), reply_markup=back_kb(lang))
    await state.set_state(AIForm.waiting_question)
    await call.answer()


@router.message(AIForm.waiting_question, F.text & ~F.text.startswith("/"))
async def ai_question_received(message: Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    await state.clear()

    now = time.monotonic()
    last = _ai_last_call.get(message.from_user.id, 0)
    remaining = AI_COOLDOWN_SECONDS - (now - last)
    if remaining > 0:
        await message.answer(t("ai_cooldown", lang, seconds=int(remaining) + 1))
        return
    _ai_last_call[message.from_user.id] = now

    thinking = await message.answer(t("ai_thinking", lang))
    question = message.text.strip()[:2000]
    try:
        # Ground the answer in the bot's own FAQ when the question looks
        # related to it; llm.ask() falls back to an open-ended answer when
        # knowledge_base.search() finds nothing relevant.
        context_docs = knowledge_base.search(question)
        answer = await llm.ask(question, context=context_docs)
        await thinking.edit_text(answer)
    except llm.LLMError as e:
        log.warning("LLM call failed: %s", e)
        await thinking.edit_text(t("ai_error", lang, error=str(e)))
    except Exception:
        log.exception("unexpected AI error")
        await thinking.edit_text(t("ai_error", lang, error="unexpected error"))


# ---------- Telegram Stars payment (native, no external provider needed) ----------
@router.callback_query(F.data == "menu:stars")
async def cb_stars(call: CallbackQuery, bot: Bot):
    lang = await db.get_lang(call.from_user.id)
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title=t("stars_title", lang),
        description=t("stars_description", lang, price=STARS_PRICE),
        payload="support-donation",
        provider_token="",  # empty string is required for Telegram Stars (XTR)
        currency="XTR",
        prices=[LabeledPrice(label=t("stars_label", lang), amount=STARS_PRICE)],
    )
    await call.answer()


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_q: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    lang = await db.get_lang(message.from_user.id)
    await message.answer(t("stars_thanks", lang))
