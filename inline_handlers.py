import asyncio
import logging

import aiohttp
from aiogram import Router
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from handlers import _geocode_city, _fetch_weather, _uah_rate
from i18n import weather_desc

router = Router()
log = logging.getLogger("bot.inline")

_CURRENCY_TRIGGERS = {"usd", "eur", "курс", "currency", "долар", "євро", "евро"}


async def _weather_result(city: str) -> InlineQueryResultArticle | None:
    async with aiohttp.ClientSession() as session:
        place = await _geocode_city(session, city)
        if not place:
            return None
        current = await _fetch_weather(session, place["latitude"], place["longitude"])
    if not current:
        return None
    label = place.get("name", city)
    country = place.get("country_code", "")
    full_label = f"{label}, {country}" if country else label
    text = (
        f"📍 {full_label}\n🌡 {current.get('temperature')}°C, "
        f"wind {current.get('windspeed')} km/h\n{weather_desc(current.get('weathercode', -1), 'en')}"
    )
    return InlineQueryResultArticle(
        id="weather",
        title=f"Weather in {full_label}",
        description=text.replace("\n", " · "),
        input_message_content=InputTextMessageContent(message_text=text),
    )


async def _currency_result() -> InlineQueryResultArticle:
    async with aiohttp.ClientSession() as session:
        usd, eur = await asyncio.gather(_uah_rate(session, "USD"), _uah_rate(session, "EUR"))
    text = f"💱 1 USD ≈ {usd:.2f} UAH\n💱 1 EUR ≈ {eur:.2f} UAH"
    return InlineQueryResultArticle(
        id="currency",
        title="USD / EUR to UAH",
        description=text.replace("\n", " · "),
        input_message_content=InputTextMessageContent(message_text=text),
    )


@router.inline_query()
async def inline_query_handler(inline_query: InlineQuery):
    query = inline_query.query.strip()
    results = []
    try:
        if not query:
            results = [
                InlineQueryResultArticle(
                    id="help",
                    title="Type a city name, or 'usd' for exchange rates",
                    description="e.g. 'Kyiv' for weather, 'usd' for currency rates",
                    input_message_content=InputTextMessageContent(
                        message_text="Type a city name for weather, or 'usd' for exchange rates."
                    ),
                )
            ]
        elif query.lower() in _CURRENCY_TRIGGERS:
            results = [await _currency_result()]
        else:
            result = await _weather_result(query)
            results = [result] if result else []
    except Exception:
        log.exception("inline query failed")
        results = []

    await inline_query.answer(results, cache_time=60, is_personal=False)
