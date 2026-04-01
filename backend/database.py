"""SQLite 연결 관리 및 테이블 초기화."""

import os
from pathlib import Path

import aiosqlite

DB_PATH = os.environ.get("PROMPTS_DB_PATH", str(Path(__file__).parent.parent / "prompts.db"))

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS prompts (
    id         TEXT PRIMARY KEY,
    title      TEXT NOT NULL,
    category   TEXT NOT NULL,
    content    TEXT NOT NULL,
    tags       TEXT NOT NULL DEFAULT '[]',
    role       TEXT DEFAULT '',
    type       TEXT DEFAULT 'prompt',
    origin     TEXT DEFAULT '',
    source     TEXT DEFAULT '',
    file_path  TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_prompts_category ON prompts(category);
CREATE INDEX IF NOT EXISTS idx_prompts_updated ON prompts(updated_at);

CREATE TABLE IF NOT EXISTS versions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id      TEXT NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
    title          TEXT NOT NULL,
    content        TEXT NOT NULL,
    tags           TEXT NOT NULL DEFAULT '[]',
    version_number INTEGER NOT NULL,
    created_at     TEXT NOT NULL,
    change_summary TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_versions_prompt ON versions(prompt_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_versions_unique
    ON versions(prompt_id, version_number);

CREATE TABLE IF NOT EXISTS suggestions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id       TEXT NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
    original_content TEXT NOT NULL,
    suggested_content TEXT NOT NULL,
    reason          TEXT NOT NULL,
    status          TEXT DEFAULT 'pending',
    requested_by    TEXT,
    created_at      TEXT NOT NULL,
    resolved_at     TEXT
);

CREATE INDEX IF NOT EXISTS idx_suggestions_prompt ON suggestions(prompt_id);
CREATE INDEX IF NOT EXISTS idx_suggestions_status ON suggestions(prompt_id, status);
"""


async def init_db(db_path: str = DB_PATH) -> None:
    """테이블과 인덱스를 생성한다. 앱 시작 시 호출."""
    async with aiosqlite.connect(db_path) as db:
        await db.executescript(SCHEMA_SQL)
        await db.commit()


async def get_db(db_path: str = DB_PATH):
    """FastAPI 의존성 주입용 async generator."""
    db = await aiosqlite.connect(db_path)
    await db.execute("PRAGMA foreign_keys = ON")
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()
