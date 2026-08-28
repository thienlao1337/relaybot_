import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

_raw_admin_id = (os.getenv("ADMIN_ID", "0") or "0").strip()
try:
    ADMIN_ID = int(_raw_admin_id)
except ValueError:
    print(
        f"WARNING: ADMIN_ID={_raw_admin_id!r} is not a number (it should be your numeric "
        "Telegram user id from @userinfobot, not a link or username) - /broadcast disabled."
    )
    ADMIN_ID = 0

RUN_MODE = os.getenv("RUN_MODE", "polling")  # "polling" (local/demo) or "webhook" (Render)

# --- webhook-mode only settings ---
# Cleaned up defensively: strips whitespace/accidental quotes, adds "https://" if the
# scheme was left off, and drops a trailing slash - these are the most common ways
# people mistype this value when pasting it from the Render dashboard.
_raw_webhook_host = os.getenv("WEBHOOK_HOST", "").strip().strip('"').strip("'").rstrip("/")
if _raw_webhook_host and not _raw_webhook_host.startswith(("http://", "https://")):
    _raw_webhook_host = "https://" + _raw_webhook_host
WEBHOOK_HOST = _raw_webhook_host  # e.g. https://your-app.onrender.com
WEBHOOK_PATH = "/webhook/" + BOT_TOKEN[-12:] if BOT_TOKEN else "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}" if WEBHOOK_HOST else ""
PORT = int(os.getenv("PORT", "8080"))

DB_PATH = os.getenv("DB_PATH", "bot.db")

# --- Mini App (Telegram WebApp) ---
WEBAPP_PATH = "/app"
WEBAPP_URL = f"{WEBHOOK_HOST}{WEBAPP_PATH}" if WEBHOOK_HOST else ""

# --- AI assistant (optional - feature disables itself if no key is set) ---
# Checked in this order: Gemini (has a genuinely free tier) -> Anthropic -> OpenAI.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
AI_ENABLED = bool(GEMINI_API_KEY or ANTHROPIC_API_KEY or OPENAI_API_KEY)
AI_COOLDOWN_SECONDS = int(os.getenv("AI_COOLDOWN_SECONDS", "20"))

# --- Payments (Telegram Stars - no external provider needed) ---
# Stars payments use currency "XTR" and an empty provider_token by design.
STARS_PRICE = int(os.getenv("STARS_PRICE", "1"))  # amount in Telegram Stars

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN is not set. Get one from @BotFather in Telegram and put it in your .env file."
    )
