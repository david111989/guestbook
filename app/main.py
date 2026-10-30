from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.config import settings

# Миграция обратно совместима: только "IF NOT EXISTS" и добавление колонок,
# ничего не удаляем и не переименовываем. Поэтому старая версия сервиса
# спокойно работает на базе, которую уже обновила новая версия.
MIGRATION = """
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    author TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


def get_connection() -> psycopg.Connection:
    return psycopg.connect(settings.database_url)


@asynccontextmanager
async def lifespan(app: FastAPI):
    with get_connection() as conn:
        conn.execute(MIGRATION)
    yield


app = FastAPI(title="Guestbook", version=settings.app_version, lifespan=lifespan)


class MessageIn(BaseModel):
    author: str = Field(min_length=1, max_length=100)
    text: str = Field(min_length=1, max_length=1000)


@app.get("/health")
def health() -> dict:
    """Проверка, что сервис жив. База не трогается."""
    return {"status": "ok"}


@app.get("/version")
def version() -> dict:
    return {"version": settings.app_version}


@app.get("/messages")
def list_messages() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, author, text, created_at FROM messages ORDER BY id DESC LIMIT 50"
        ).fetchall()
    return [
        {"id": r[0], "author": r[1], "text": r[2], "created_at": r[3].isoformat()}
        for r in rows
    ]


@app.post("/messages", status_code=201)
def add_message(message: MessageIn) -> dict:
    with get_connection() as conn:
        row = conn.execute(
            "INSERT INTO messages (author, text) VALUES (%s, %s) RETURNING id",
            (message.author, message.text),
        ).fetchone()
    return {"id": row[0]}
