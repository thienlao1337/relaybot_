import aiosqlite
from datetime import datetime, timezone

from config import DB_PATH

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    lang TEXT NOT NULL DEFAULT 'ua',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    done INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
"""


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(_SCHEMA)
        await db.commit()


def _now():
    return datetime.now(timezone.utc).isoformat()


async def ensure_user(user_id: int, default_lang: str = "ua") -> str:
    """Create the user row if missing. Returns the user's current language."""
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        if row:
            return row[0]
        await db.execute(
            "INSERT INTO users (user_id, lang, created_at) VALUES (?, ?, ?)",
            (user_id, default_lang, _now()),
        )
        await db.commit()
        return default_lang


async def set_lang(user_id: int, lang: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET lang = ? WHERE user_id = ?", (lang, user_id))
        await db.commit()


async def get_lang(user_id: int) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        return row[0] if row else "ua"


async def all_user_ids() -> list[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT user_id FROM users")
        rows = await cur.fetchall()
        return [r[0] for r in rows]


async def add_task(user_id: int, text: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO tasks (user_id, text, done, created_at) VALUES (?, ?, 0, ?)",
            (user_id, text, _now()),
        )
        await db.commit()
        return cur.lastrowid


async def list_tasks(user_id: int, include_done: bool = False):
    async with aiosqlite.connect(DB_PATH) as db:
        if include_done:
            cur = await db.execute(
                "SELECT id, text, done FROM tasks WHERE user_id = ? ORDER BY id DESC", (user_id,)
            )
        else:
            cur = await db.execute(
                "SELECT id, text, done FROM tasks WHERE user_id = ? AND done = 0 ORDER BY id DESC",
                (user_id,),
            )
        return await cur.fetchall()


async def complete_task(user_id: int, task_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE tasks SET done = 1 WHERE id = ? AND user_id = ?", (task_id, user_id)
        )
        await db.commit()


async def delete_task(user_id: int, task_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
        await db.commit()
