"""Thin wrapper around Anthropic / OpenAI chat APIs, called with plain aiohttp
(no extra SDK dependency). Anthropic is tried first if both keys are set.
"""

import aiohttp

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)

SYSTEM_PROMPT = (
    "You are a concise, friendly assistant embedded in a Telegram bot. "
    "Answer in 2-4 short sentences unless the user clearly asks for more detail. "
    "Reply in the same language the user wrote in."
)


class LLMError(Exception):
    pass


async def _ask_gemini(question: str) -> str:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {
        "contents": [{"parts": [{"text": question}]}],
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, timeout=30) as resp:
            data = await resp.json()
            if resp.status != 200:
                raise LLMError(data.get("error", {}).get("message", f"HTTP {resp.status}"))
            candidates = data.get("candidates") or []
            if not candidates:
                raise LLMError("empty response")
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts)
            return text.strip() or "…"


async def _ask_anthropic(question: str) -> str:
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 400,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": question}],
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload, timeout=30) as resp:
            data = await resp.json()
            if resp.status != 200:
                raise LLMError(data.get("error", {}).get("message", f"HTTP {resp.status}"))
            parts = data.get("content", [])
            text = "".join(p.get("text", "") for p in parts if p.get("type") == "text")
            return text.strip() or "…"


async def _ask_openai(question: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "content-type": "application/json",
    }
    payload = {
        "model": OPENAI_MODEL,
        "max_tokens": 400,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload, timeout=30) as resp:
            data = await resp.json()
            if resp.status != 200:
                raise LLMError(data.get("error", {}).get("message", f"HTTP {resp.status}"))
            choices = data.get("choices", [])
            if not choices:
                raise LLMError("empty response")
            return choices[0]["message"]["content"].strip()


async def ask(question: str) -> str:
    if GEMINI_API_KEY:
        return await _ask_gemini(question)
    if ANTHROPIC_API_KEY:
        return await _ask_anthropic(question)
    if OPENAI_API_KEY:
        return await _ask_openai(question)
    raise LLMError("no API key configured")
