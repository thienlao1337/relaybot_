# Relay Assistant Bot

A Telegram bot built with aiogram 3: a task manager, weather and exchange rates from open APIs,
an LLM-powered assistant that answers from a knowledge base (RAG), background exchange-rate alerts,
a built-in web interface (Telegram Mini App) with an admin panel, payments via Telegram Stars,
and inline mode (`@bot query` in any chat).

## Features

- 📝 Tasks that persist between sessions
- 🌦 Weather by city name (open-meteo.com, no API key needed)
- 💱 Exchange rates against the hryvnia (open.er-api.com, no API key needed)
- 🔔 Rate alerts — "notify me when USD goes above/below X": a background job polls the rates and
  sends a notification as soon as the threshold is crossed (see `watch_service.py`)
- 🤖 AI assistant on top of Gemini (free), Anthropic Claude or OpenAI (optional, with your own
  API key), with retrieval-augmented answers: questions about the bot itself are answered strictly
  from the built-in knowledge base (`knowledge_base.py`) instead of being made up — if the answer
  isn't there, the bot says so
- 🖥 Mini App — four tabs (tasks, weather, rates, admin) as a full web interface inside Telegram,
  with request authentication using Telegram's official `initData` validation algorithm
- 🛠 Admin panel in the Mini App (visible only to `ADMIN_ID`): user/task/alert statistics and
  broadcasting to all users straight from the interface
- ⭐ Payments via Telegram Stars — Telegram's native currency, no third-party provider
- 🔎 Inline mode: `@your_bot Kyiv` or `@your_bot usd` works in any chat, not just in the bot's DM
- 🌐 Interface language switchable on the fly (Ukrainian / English / Russian); new users start in
  their Telegram app language, and the Mini App follows the language chosen in the bot
- 🔐 `/broadcast` and the admin API endpoints are restricted to the administrator
- 🗄 SQLite out of the box, switch to PostgreSQL with a single environment variable (see below)
- ⚙️ The same code runs in long-polling mode (local) and webhook mode (production)

## Stack

Python 3.12 · [aiogram 3](https://docs.aiogram.dev/) · aiohttp · SQLAlchemy 2 (async) ·
SQLite / PostgreSQL · Docker

## Running locally

1. Get a bot token from [@BotFather](https://t.me/BotFather): `/newbot` and follow the prompts.
2. Copy `.env.example` to `.env` and put your token in:
   ```
   cp .env.example .env
   ```
3. Install dependencies and start the bot:
   ```
   pip install -r requirements.txt
   python main.py
   ```
4. Send `/start` to your bot in Telegram.

Locally (`RUN_MODE=polling`) the only features unavailable are the ones that need a public HTTPS
address — the Mini App and the webhook. Tasks, weather, rates, the AI assistant, Stars payments and
inline mode all work.

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `BOT_TOKEN` | yes | token from @BotFather |
| `ADMIN_ID` | no | your numeric Telegram id (for `/broadcast`), get it from @userinfobot |
| `GEMINI_API_KEY` | no | enables the AI assistant via Google Gemini — **free tier, no card needed**, checked first |
| `ANTHROPIC_API_KEY` | no | enables the AI assistant via Claude (paid, used if no Gemini key is set) |
| `OPENAI_API_KEY` | no | enables the AI assistant via OpenAI (paid, used if neither of the above is set) |
| `STARS_PRICE` | no | price of the demo payment in Telegram Stars, default `1` |
| `WEBHOOK_HOST` | webhook mode only | public HTTPS address of the service; the Mini App URL is built from it too |
| `DATABASE_URL` | no | PostgreSQL connection string; if unset, SQLite at `DB_PATH` is used |
| `PRICE_WATCH_ENABLED` | no | `true`/`false`, background rate polling for alerts, on by default |

If none of the three AI keys is set, the AI assistant button stays in the menu but replies that the
feature isn't configured, instead of throwing an error.

The free option is **Gemini**: get an API key in Google AI Studio (aistudio.google.com), no card
required. Note that Google may use free-tier data to improve its models — if that matters, use a
paid tier or Anthropic/OpenAI.

### If the AI assistant fails with "model ... is no longer available"

Providers periodically retire old model versions. If the bot returns an error like
`model X is no longer available, use model Y instead`, the quickest fix is to set the model through
an environment variable (on Render: Environment → Add Environment Variable) and redeploy — no code
changes needed:

| Provider | Variable | Default in code at the time of writing |
|---|---|---|
| Gemini | `GEMINI_MODEL` | `gemini-3.5-flash-lite` |
| Anthropic | `ANTHROPIC_MODEL` | `claude-haiku-4-5-20251001` |
| OpenAI | `OPENAI_MODEL` | `gpt-5.6-luna` |

Take the value from the error message (providers usually suggest the current id) or from the
provider's documentation. If the error keeps coming up for fresh deployments, update the defaults in
`config.py` as well.

## PostgreSQL instead of SQLite

By default the bot writes to an SQLite file — nothing to configure, fine for local development and
demos. For production one variable is enough:

1. Create a database (e.g. a free Render Postgres, or any other provider).
2. Paste the connection string (`postgres://...` or `postgresql://...`) into `DATABASE_URL` as-is —
   the scheme is normalized automatically for the asyncpg driver.
3. Redeploy. `db.py` uses SQLAlchemy 2 (async ORM), so models and queries are the same for SQLite
   and Postgres; tables are created automatically on startup (`init_db()`).

Existing SQLite data is not migrated automatically. A real production setup with historical data
would need a separate migration (e.g. with `pgloader` or export/import), which is intentionally out
of scope for this demo project.

## Rate alerts and background jobs

`watch_service.py` is a separate `asyncio` loop that polls exchange rates every 5 minutes, notifies
users whose thresholds (`/watch` or the "🔔 Rate alert" button) were crossed, and then deactivates the
triggered alert. It runs as a background task on the same event loop as the bot, so no separate worker
or task queue is needed — see `main.py`.

On Render's free plan this means the service won't fall asleep on its own (usually a plus for a bot,
but it uses up free-plan hours faster). Turn it off with `PRICE_WATCH_ENABLED=false`.

## Deployment

The project is ready to deploy to [Render](https://render.com) as a Docker Web Service — the
configuration is in `render.yaml` and `Dockerfile`.

1. Push the repository and connect it in Render (New → Web Service).
2. Add the environment variables you need from the table above.
3. After the first deploy, copy the Render URL into `WEBHOOK_HOST` (no trailing slash). The service
   redeploys, registers the webhook, and the Mini App becomes available via the "Open mini app" button.
4. Enable inline mode in @BotFather: `/setinline` → pick the bot → enter any placeholder text
   (e.g. "Type a city or usd").

On Render's free plan the service sleeps after ~15 minutes without requests and wakes up on the
first incoming message within 30–60 seconds — Telegram simply retries delivery in the meantime.
For an instance that never sleeps, use a paid Render plan or any VPS.

## Project structure

```
config.py            — configuration from environment variables
db.py                — storage layer (async SQLAlchemy): users, tasks, alerts, statistics
knowledge_base.py    — small knowledge base and search over it for the assistant's RAG answers
watch_service.py     — background loop polling rates and sending alert notifications
i18n.py              — interface texts in three languages
handlers.py          — handlers, keyboards, business logic (tasks, weather, rates, alerts, AI, Stars)
inline_handlers.py   — inline-mode handler
llm.py               — wrapper over the Gemini / Anthropic / OpenAI chat APIs, with RAG context
security.py          — Telegram WebApp initData validation
webapp_page.py       — HTML/JS of the Telegram Mini App, including the admin tab
api.py               — REST endpoints for the Mini App, including /api/admin/*
main.py              — entry point: polling or webhook (selected by RUN_MODE)
Dockerfile           — image for deployment
render.yaml          — Render service configuration
```

## License

MIT
