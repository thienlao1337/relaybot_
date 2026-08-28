"""Storage layer, built on SQLAlchemy's async ORM.

The point of using SQLAlchemy here instead of raw aiosqlite is that the same
models and queries below run unchanged against SQLite (zero setup, good for
local dev and small demos) or PostgreSQL (production) - the only thing that
changes is the DATABASE_URL environment variable. See config.py for how that
URL is built/normalized.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    delete,
    func,
    select,
    update,
)
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config import DATABASE_URL


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    lang: Mapped[str] = mapped_column(String(2), nullable=False, default="ua")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    text: Mapped[str] = mapped_column(String(200), nullable=False)
    done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class Watcher(Base):
    """A one-shot currency-rate alert: notify the user once UAH/<currency>
    crosses <threshold> in <direction>, then deactivate itself."""

    __tablename__ = "watchers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)  # "USD" | "EUR"
    direction: Mapped[str] = mapped_column(String(5), nullable=False)  # "above" | "below"
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


_engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
_Session = async_sessionmaker(_engine, expire_on_commit=False)


async def init_db():
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ---------- users ----------
async def ensure_user(user_id: int, default_lang: str = "ua") -> str:
    """Create the user row if missing. Returns the user's current language."""
    async with _Session() as session:
        user = await session.get(User, user_id)
        if user:
            return user.lang
        session.add(User(user_id=user_id, lang=default_lang))
        await session.commit()
        return default_lang


async def set_lang(user_id: int, lang: str):
    async with _Session() as session:
        user = await session.get(User, user_id)
        if user:
            user.lang = lang
            await session.commit()


async def get_lang(user_id: int) -> str:
    async with _Session() as session:
        user = await session.get(User, user_id)
        return user.lang if user else "ua"


async def all_user_ids() -> list[int]:
    async with _Session() as session:
        result = await session.execute(select(User.user_id))
        return [row[0] for row in result.all()]


# ---------- tasks ----------
async def add_task(user_id: int, text: str) -> int:
    async with _Session() as session:
        task = Task(user_id=user_id, text=text, done=False)
        session.add(task)
        await session.commit()
        return task.id


async def list_tasks(user_id: int, include_done: bool = False):
    async with _Session() as session:
        stmt = select(Task.id, Task.text, Task.done).where(Task.user_id == user_id)
        if not include_done:
            stmt = stmt.where(Task.done.is_(False))
        stmt = stmt.order_by(Task.id.desc())
        result = await session.execute(stmt)
        return result.all()


async def complete_task(user_id: int, task_id: int):
    async with _Session() as session:
        await session.execute(
            update(Task).where(Task.id == task_id, Task.user_id == user_id).values(done=True)
        )
        await session.commit()


async def delete_task(user_id: int, task_id: int):
    async with _Session() as session:
        await session.execute(delete(Task).where(Task.id == task_id, Task.user_id == user_id))
        await session.commit()


# ---------- price watchers ----------
async def add_watcher(user_id: int, currency: str, direction: str, threshold: float) -> int:
    async with _Session() as session:
        watcher = Watcher(
            user_id=user_id, currency=currency, direction=direction, threshold=threshold, active=True
        )
        session.add(watcher)
        await session.commit()
        return watcher.id


async def list_user_watchers(user_id: int):
    async with _Session() as session:
        stmt = (
            select(Watcher.id, Watcher.currency, Watcher.direction, Watcher.threshold)
            .where(Watcher.user_id == user_id, Watcher.active.is_(True))
            .order_by(Watcher.id.desc())
        )
        result = await session.execute(stmt)
        return result.all()


async def delete_watcher(user_id: int, watcher_id: int):
    async with _Session() as session:
        await session.execute(
            delete(Watcher).where(Watcher.id == watcher_id, Watcher.user_id == user_id)
        )
        await session.commit()


async def list_active_watchers() -> list[Watcher]:
    """Detached copies of every still-active watcher, for the background loop."""
    async with _Session() as session:
        result = await session.execute(select(Watcher).where(Watcher.active.is_(True)))
        return list(result.scalars().all())


async def deactivate_watcher(watcher_id: int):
    async with _Session() as session:
        await session.execute(update(Watcher).where(Watcher.id == watcher_id).values(active=False))
        await session.commit()


# ---------- admin stats ----------
async def get_stats() -> dict:
    async with _Session() as session:
        total_users = (await session.execute(select(func.count()).select_from(User))).scalar_one()
        total_tasks = (await session.execute(select(func.count()).select_from(Task))).scalar_one()
        done_tasks = (
            await session.execute(
                select(func.count()).select_from(Task).where(Task.done.is_(True))
            )
        ).scalar_one()
        lang_rows = (
            await session.execute(select(User.lang, func.count()).group_by(User.lang))
        ).all()
        active_watchers = (
            await session.execute(
                select(func.count()).select_from(Watcher).where(Watcher.active.is_(True))
            )
        ).scalar_one()
        return {
            "total_users": total_users,
            "total_tasks": total_tasks,
            "done_tasks": done_tasks,
            "active_tasks": total_tasks - done_tasks,
            "by_lang": {lang: count for lang, count in lang_rows},
            "active_watchers": active_watchers,
        }
