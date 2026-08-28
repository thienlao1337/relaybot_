"""Thin wrapper around Gemini / Anthropic / OpenAI chat APIs, called with plain
aiohttp (no extra SDK dependency). Gemini is tried first if all three keys are
set (it has a genuinely free tier), then Anthropic, then OpenAI.
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
from knowledge_base import Document

BASE_SYSTEM_PROMPT = (
    "You are a concise, friendly assistant embedded in a Telegram bot. "
    "Answer in 2-4 short sentences unless the user clearly asks for more detail. "
    "Reply in the same language the user wrote in."
)

# Used only when retrieval found relevant documents (see knowledge_base.py).
# Keeps the model from inventing details that aren't actually in the context -
# the whole point of grounding an answer in a knowledge base is that it's
# allowed to say "I don't know" instead of hallucinating.
GROUNDED_SYSTEM_PROMPT = (
    BASE_SYSTEM_PROMPT + "\n\n"
    "Answer the user's question using ONLY the context below. If the context "
    "doesn't contain the answer, say plainly that you're not sure rather than "
    "guessing, and suggest the user rephrase or ask something else.\n\n"
    "Context:\n{context}"
)


class LLMError(Exception):
    pass


def _build_system_prompt(context: list[Document] | None) -> str:
    if not context:
        return BASE_SYSTEM_PROMPT
    context_text = "\n\n".join(f"### {doc.title}\n{doc.text}" for doc in context)
    return GROUNDED_SYSTEM_PROMPT.format(context=context_text)


async def _ask_gemini(question: str, system_prompt: str) -> str:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {
        "contents": [{"parts": [{"text": question}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
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


async def _ask_anthropic(question: str, system_prompt: str) -> str:
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 400,
        "system": system_prompt,
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


async def _ask_openai(question: str, system_prompt: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "content-type": "application/json",
    }
    payload = {
        "model": OPENAI_MODEL,
        "max_tokens": 400,
        "messages": [
            {"role": "system", "content": system_prompt},
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


async def ask(question: str, context: list[Document] | None = None) -> str:
    """Ask the configured LLM provider. When `context` (from
    knowledge_base.search) is non-empty, the model is instructed to answer
    only from it and to say so honestly when it can't."""
    system_prompt = _build_system_prompt(context)
    if GEMINI_API_KEY:
        return await _ask_gemini(question, system_prompt)
    if ANTHROPIC_API_KEY:
        return await _ask_anthropic(question, system_prompt)
    if OPENAI_API_KEY:
        return await _ask_openai(question, system_prompt)
    raise LLMError("no API key configured")
