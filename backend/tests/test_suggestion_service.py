"""Unit tests for suggestion_service: CRUD with real aiosqlite in-memory DB."""

import os
import tempfile

import aiosqlite
import pytest
import pytest_asyncio

from backend.database import init_db
from backend.services.prompt_service import create_prompt, get_prompt
from backend.services.suggestion_service import (
    ConflictError,
    accept_suggestion,
    create_suggestion,
    list_suggestions,
    reject_suggestion,
)
from backend.models import PromptCreate


@pytest_asyncio.fixture
async def db():
    """In-memory-like temp DB with full schema."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    await init_db(db_path=db_path)

    conn = await aiosqlite.connect(db_path)
    await conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = aiosqlite.Row
    yield conn
    await conn.close()
    os.unlink(db_path)


async def _create_sample_prompt(db, prompt_id="rca-test", content="# Original"):
    """Helper: create a prompt and return it."""
    data = PromptCreate(
        id=prompt_id,
        title="Test Prompt",
        category="rca",
        content=content,
        tags=["test"],
    )
    return await create_prompt(db, data)


def _ai_result(content="# Original", improved="# Improved", reason="Better clarity"):
    return {
        "original_content": content,
        "improved_content": improved,
        "reason": reason,
    }


# ── create_suggestion ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_suggestion(db):
    """Happy path: suggestion is created and persisted."""
    prompt = await _create_sample_prompt(db)
    result = _ai_result(content=prompt.content)
    suggestion = await create_suggestion(db, prompt.id, result)

    assert suggestion.prompt_id == prompt.id
    assert suggestion.suggested_content == "# Improved"
    assert suggestion.reason == "Better clarity"
    assert suggestion.status == "pending"
    assert suggestion.original_content == prompt.content

    # Verify it's in the DB
    cursor = await db.execute("SELECT COUNT(*) FROM suggestions WHERE prompt_id = ?", (prompt.id,))
    row = await cursor.fetchone()
    assert row[0] == 1


@pytest.mark.asyncio
async def test_create_suggestion_prompt_not_found(db):
    """Suggestion references a prompt_id -- foreign key constraint handles missing prompt."""
    result = _ai_result()
    # Foreign key constraint will raise
    with pytest.raises(Exception):
        await create_suggestion(db, "nonexistent-id", result)


@pytest.mark.asyncio
async def test_create_suggestion_pending_exists(db):
    """If a pending suggestion exists, return it instead of creating a new one."""
    prompt = await _create_sample_prompt(db)
    result = _ai_result(content=prompt.content)

    first = await create_suggestion(db, prompt.id, result)
    second = await create_suggestion(db, prompt.id, result)

    assert first.id == second.id
    # Verify only 1 row exists
    cursor = await db.execute("SELECT COUNT(*) FROM suggestions WHERE prompt_id = ?", (prompt.id,))
    row = await cursor.fetchone()
    assert row[0] == 1


# ── accept_suggestion ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_accept_suggestion(db):
    """Accept updates prompt content and creates a version."""
    prompt = await _create_sample_prompt(db)
    result = _ai_result(content=prompt.content, improved="# Accepted Content")
    suggestion = await create_suggestion(db, prompt.id, result)

    accepted = await accept_suggestion(db, suggestion.id)

    assert accepted.status == "accepted"
    assert accepted.resolved_at is not None

    # Verify prompt was updated
    updated_prompt = await get_prompt(db, prompt.id)
    assert updated_prompt.content == "# Accepted Content"

    # Verify a version was created (the pre-accept state)
    cursor = await db.execute("SELECT COUNT(*) FROM versions WHERE prompt_id = ?", (prompt.id,))
    row = await cursor.fetchone()
    assert row[0] >= 1


@pytest.mark.asyncio
async def test_accept_suggestion_not_found(db):
    """Accepting a nonexistent suggestion raises ValueError."""
    with pytest.raises(ValueError, match="not found"):
        await accept_suggestion(db, 9999)


@pytest.mark.asyncio
async def test_accept_suggestion_already_resolved(db):
    """Accepting an already-accepted suggestion raises ValueError."""
    prompt = await _create_sample_prompt(db)
    result = _ai_result(content=prompt.content)
    suggestion = await create_suggestion(db, prompt.id, result)

    await accept_suggestion(db, suggestion.id)

    with pytest.raises(ValueError, match="already"):
        await accept_suggestion(db, suggestion.id)


@pytest.mark.asyncio
async def test_accept_suggestion_content_conflict(db):
    """If prompt content changed since suggestion was created, raise ConflictError."""
    prompt = await _create_sample_prompt(db)
    result = _ai_result(content=prompt.content)
    suggestion = await create_suggestion(db, prompt.id, result)

    # Modify the prompt content directly (simulating another edit)
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        "UPDATE prompts SET content = ?, updated_at = ? WHERE id = ?",
        ("# Changed content", now, prompt.id),
    )
    await db.commit()

    with pytest.raises(ConflictError, match="changed"):
        await accept_suggestion(db, suggestion.id)


# ── reject_suggestion ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_reject_suggestion(db):
    """Rejecting a pending suggestion sets status to rejected."""
    prompt = await _create_sample_prompt(db)
    result = _ai_result(content=prompt.content)
    suggestion = await create_suggestion(db, prompt.id, result)

    rejected = await reject_suggestion(db, suggestion.id)

    assert rejected.status == "rejected"
    assert rejected.resolved_at is not None


@pytest.mark.asyncio
async def test_reject_suggestion_already_resolved(db):
    """Rejecting an already-rejected suggestion raises ValueError."""
    prompt = await _create_sample_prompt(db)
    result = _ai_result(content=prompt.content)
    suggestion = await create_suggestion(db, prompt.id, result)

    await reject_suggestion(db, suggestion.id)

    with pytest.raises(ValueError, match="already"):
        await reject_suggestion(db, suggestion.id)


# ── list_suggestions ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_suggestions(db):
    """Returns suggestions filtered by prompt_id."""
    p1 = await _create_sample_prompt(db, prompt_id="rca-one", content="Content 1")
    p2 = await _create_sample_prompt(db, prompt_id="rca-two", content="Content 2")

    await create_suggestion(db, p1.id, _ai_result(content=p1.content, improved="I1"))
    # Mark p1's suggestion as accepted so we can create another for p1
    suggestions_p1 = await list_suggestions(db, p1.id)
    await accept_suggestion(db, suggestions_p1[0].id)
    await create_suggestion(db, p1.id, _ai_result(content="I1", improved="I1b"))

    await create_suggestion(db, p2.id, _ai_result(content=p2.content, improved="I2"))

    result_p1 = await list_suggestions(db, p1.id)
    result_p2 = await list_suggestions(db, p2.id)

    assert len(result_p1) == 2
    assert len(result_p2) == 1
    assert all(s.prompt_id == p1.id for s in result_p1)
    assert all(s.prompt_id == p2.id for s in result_p2)
