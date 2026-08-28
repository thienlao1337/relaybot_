"""A minimal retrieval-augmented-generation (RAG) layer for the AI assistant.

Real RAG setups embed documents with a vector model and search with cosine
similarity against a vector database (pgvector, Pinecone, Qdrant, ...). That's
overkill for a handful of short FAQ entries, and it would mean shipping an API
key or a heavy local model just for this demo. So this module implements the
same *shape* of the pattern - retrieve relevant chunks, then force the model to
answer only from them - with plain keyword-overlap scoring over an in-memory
list of documents. Swapping in real embeddings later only means replacing
`search()`'s body; every caller (llm.py, handlers.py) is unaffected.

DOCUMENTS below describes this bot itself. In a client project it would be
their product FAQ, policy pages, or catalog instead.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_WORD_RE = re.compile(r"[a-zA-Zа-яА-ЯіїєґІЇЄҐ0-9]+")

# Minimum fraction of the query's words that must appear in a document before
# it's considered relevant enough to hand to the model. Keeps the assistant
# from bolting an unrelated FAQ entry onto the prompt just because it shares
# one common word with the question.
_MIN_SCORE = 0.15


@dataclass(frozen=True)
class Document:
    doc_id: str
    title: str
    text: str


DOCUMENTS: list[Document] = [
    Document(
        "features",
        "What this bot can do",
        "This bot is a Telegram assistant with: a persistent task list (SQLite/Postgres-backed), "
        "weather lookup by city name via Open-Meteo, USD/EUR to UAH exchange rates via "
        "open.er-api.com, an AI assistant backed by Gemini/Claude/OpenAI, a Telegram Mini App "
        "with Tasks/Weather/Currency/Admin tabs, Telegram Stars payments, inline mode "
        "(usable as @botname query in any chat), and one-shot currency-threshold alerts.",
    ),
    Document(
        "languages",
        "Supported languages",
        "The bot's interface is available in Ukrainian, English, and Russian. Users switch "
        "language any time via the Language menu or the /lang command, and every user's choice "
        "is stored and reused on their next visit.",
    ),
    Document(
        "ai_assistant",
        "How the AI assistant works",
        "The AI assistant tries Google Gemini first (it has a free tier with no credit card "
        "required), then falls back to Anthropic Claude, then OpenAI, depending on which API "
        "keys are configured. Requests are rate-limited per user with a cooldown to avoid "
        "abuse. Answers are grounded in this FAQ where relevant; if a question falls outside "
        "what's documented, the assistant says so instead of guessing.",
    ),
    Document(
        "privacy",
        "Data and privacy",
        "The bot stores only what's needed to work: your Telegram user id, chosen language, "
        "and the tasks or alerts you create. No message content is stored beyond that. "
        "Mini App requests are authenticated using Telegram's official initData signature "
        "check, so only the real logged-in user can read or change their own data.",
    ),
    Document(
        "pricing_demo",
        "About the Stars payment demo",
        "The Support button charges a small amount in Telegram Stars, Telegram's native "
        "in-app currency - there's no external payment provider involved. It's included to "
        "demonstrate a working Telegram Payments integration end to end (invoice, "
        "pre-checkout confirmation, successful-payment handling), not because the bot's other "
        "features are paid.",
    ),
    Document(
        "watchers",
        "Currency alerts (price watcher)",
        "You can ask to be notified once a currency crosses a threshold you set - for example "
        "'USD above 42'. A background job checks rates every few minutes; when a watcher's "
        "condition is met, the bot sends a message and the alert deactivates itself. This is "
        "a small demonstration of a background polling/notification pattern.",
    ),
    Document(
        "tech_stack",
        "Tech stack",
        "The bot is written in Python 3.12 with aiogram 3, aiohttp for the webhook/Mini App "
        "server, and SQLAlchemy's async ORM for storage (SQLite locally, PostgreSQL in "
        "production via a single DATABASE_URL environment variable). It runs as a Docker "
        "container and deploys to Render.",
    ),
    Document(
        "hire",
        "About the developer / hiring",
        "This bot was built as a portfolio piece to demonstrate Telegram bot development: "
        "external API integration, stateful conversations, payments, Mini Apps, and AI "
        "integration. For custom bots or automation work, get in touch through the "
        "Freelancehunt profile this bot is linked from.",
    ),
]


def _tokenize(text: str) -> set[str]:
    return {w.lower() for w in _WORD_RE.findall(text)}


def search(query: str, top_k: int = 2) -> list[Document]:
    """Return up to top_k documents whose word overlap with `query` clears
    _MIN_SCORE, best match first. Returns an empty list when nothing in the
    knowledge base looks relevant - callers should treat that as "no context",
    not silently fall back to an ungrounded answer."""
    query_words = _tokenize(query)
    if not query_words:
        return []

    scored: list[tuple[float, Document]] = []
    for doc in DOCUMENTS:
        doc_words = _tokenize(f"{doc.title} {doc.text}")
        if not doc_words:
            continue
        overlap = query_words & doc_words
        score = len(overlap) / len(query_words)
        if score >= _MIN_SCORE:
            scored.append((score, doc))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [doc for _, doc in scored[:top_k]]
