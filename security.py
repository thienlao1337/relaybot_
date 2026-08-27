"""Validates Telegram Mini App `initData` per the official algorithm:
https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""

import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

from config import BOT_TOKEN

MAX_AGE_SECONDS = 3600  # reject stale initData (defends against replay of a leaked link)


def validate_init_data(init_data: str) -> dict | None:
    """Returns the parsed data dict (with 'user' decoded to a dict) if the
    signature and freshness check pass, otherwise None."""
    if not init_data:
        return None

    pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        return None

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))

    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return None

    auth_date = pairs.get("auth_date")
    if auth_date and (time.time() - int(auth_date)) > MAX_AGE_SECONDS:
        return None

    if "user" in pairs:
        try:
            pairs["user"] = json.loads(pairs["user"])
        except (json.JSONDecodeError, TypeError):
            return None

    return pairs
