"""DB 초기화 단위 테스트: 테이블 존재, FK 제약, 인덱스 확인."""

import os
import tempfile

import aiosqlite
import pytest
import pytest_asyncio

from backend.database import init_db


@pytest_asyncio.fixture
async def db_path():
    """임시 DB 파일을 생성하고 init_db()를 실행한다."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    await init_db(db_path=path)
    yield path
    os.unlink(path)


@pytest.mark.asyncio
async def test_prompts_table_exists(db_path):
    """prompts 테이블이 생성되어야 한다. (Req 1.1)"""
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='prompts'"
        )
        row = await cursor.fetchone()
        assert row is not None, "prompts 테이블이 존재하지 않음"


@pytest.mark.asyncio
async def test_versions_table_exists(db_path):
    """versions 테이블이 생성되어야 한다. (Req 1.2)"""
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='versions'"
        )
        row = await cursor.fetchone()
        assert row is not None, "versions 테이블이 존재하지 않음"


@pytest.mark.asyncio
async def test_foreign_key_constraint(db_path):
    """존재하지 않는 prompt_id로 version 삽입 시 FK 위반 에러. (Req 1.3)"""
    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        with pytest.raises(aiosqlite.IntegrityError):
            await db.execute(
                """INSERT INTO versions
                   (prompt_id, title, content, tags, version_number, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                ("nonexistent-id", "t", "c", "[]", 1, "2024-01-01T00:00:00"),
            )
            await db.commit()


@pytest.mark.asyncio
async def test_indexes_exist(db_path):
    """설계에 명시된 인덱스가 모두 존재해야 한다."""
    expected = {
        "idx_prompts_category",
        "idx_prompts_updated",
        "idx_versions_prompt",
        "idx_versions_unique",
    }
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute(
            "SELECT name FROM sqlite_master WHERE type='index'"
        )
        rows = await cursor.fetchall()
        actual = {row[0] for row in rows}
        missing = expected - actual
        assert not missing, f"누락된 인덱스: {missing}"
