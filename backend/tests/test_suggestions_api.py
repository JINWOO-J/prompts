"""Integration tests for suggestion API endpoints via httpx AsyncClient."""

import os
import tempfile
from unittest.mock import AsyncMock, patch

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

import aiosqlite

from backend.database import init_db, get_db
from backend.routers.prompts import router as prompts_router
from backend.routers.suggestions import router as suggestions_router


@pytest_asyncio.fixture
async def app():
    """Test FastAPI app with temp DB."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    await init_db(db_path=db_path)

    test_app = FastAPI()
    test_app.include_router(prompts_router)
    test_app.include_router(suggestions_router)

    async def override_get_db():
        db = await aiosqlite.connect(db_path)
        await db.execute("PRAGMA foreign_keys = ON")
        db.row_factory = aiosqlite.Row
        try:
            yield db
        finally:
            await db.close()

    test_app.dependency_overrides[get_db] = override_get_db
    yield test_app
    os.unlink(db_path)


@pytest_asyncio.fixture
async def client(app):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


SAMPLE_PROMPT = {
    "title": "Test Prompt",
    "category": "rca",
    "content": "# Original Content",
    "tags": ["kubernetes"],
    "id": "rca-test",
}

MOCK_AI_RESULT = {
    "improved_content": "# Improved Content",
    "reason": "Better structure and clarity",
}


async def _create_prompt(client):
    """Helper: create a sample prompt."""
    resp = await client.post("/api/prompts", json=SAMPLE_PROMPT)
    assert resp.status_code == 201
    return resp.json()


async def _create_suggestion(client):
    """Helper: create a prompt + suggestion."""
    await _create_prompt(client)
    with patch(
        "backend.routers.suggestions.suggest_improvement",
        new_callable=AsyncMock,
        return_value=MOCK_AI_RESULT,
    ), patch("backend.routers.suggestions.check_ai_available", return_value=True):
        resp = await client.post("/api/prompts/rca-test/suggest")
    return resp


# ── POST /api/prompts/{id}/suggest ────────────────────────────────────


@pytest.mark.asyncio
async def test_suggest_endpoint(client):
    """POST suggest -> 201 with suggestion response."""
    resp = await _create_suggestion(client)

    assert resp.status_code == 201
    data = resp.json()
    assert data["prompt_id"] == "rca-test"
    assert data["suggested_content"] == "# Improved Content"
    assert data["reason"] == "Better structure and clarity"
    assert data["status"] == "pending"
    assert data["original_content"] == "# Original Content"


@pytest.mark.asyncio
async def test_suggest_endpoint_prompt_not_found(client):
    """POST suggest on nonexistent prompt -> 404."""
    with patch(
        "backend.routers.suggestions.suggest_improvement",
        new_callable=AsyncMock,
        return_value=MOCK_AI_RESULT,
    ), patch("backend.routers.suggestions.check_ai_available", return_value=True):
        resp = await client.post("/api/prompts/nonexistent/suggest")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_suggest_endpoint_ai_unavailable(client):
    """POST suggest when AI is unavailable -> 503."""
    await _create_prompt(client)
    with patch("backend.routers.suggestions.check_ai_available", return_value=False):
        resp = await client.post("/api/prompts/rca-test/suggest")
    assert resp.status_code == 503


# ── POST .../accept ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_accept_endpoint(client):
    """Accept suggestion -> 200, prompt content updated."""
    resp = await _create_suggestion(client)
    suggestion = resp.json()
    sid = suggestion["id"]

    resp = await client.post(f"/api/prompts/rca-test/suggestions/{sid}/accept")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "accepted"

    # Verify prompt was updated
    resp = await client.get("/api/prompts/rca-test")
    assert resp.json()["content"] == "# Improved Content"


@pytest.mark.asyncio
async def test_accept_endpoint_conflict(client):
    """Accept after prompt content changed -> 409."""
    resp = await _create_suggestion(client)
    suggestion = resp.json()
    sid = suggestion["id"]

    # Change the prompt content
    await client.put("/api/prompts/rca-test", json={"content": "# Modified"})

    resp = await client.post(f"/api/prompts/rca-test/suggestions/{sid}/accept")
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_accept_endpoint_already_resolved(client):
    """Accept an already-accepted suggestion -> 400."""
    resp = await _create_suggestion(client)
    suggestion = resp.json()
    sid = suggestion["id"]

    await client.post(f"/api/prompts/rca-test/suggestions/{sid}/accept")
    resp = await client.post(f"/api/prompts/rca-test/suggestions/{sid}/accept")
    # Already resolved -> ValueError in service -> 400
    assert resp.status_code == 400


# ── POST .../reject ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_reject_endpoint(client):
    """Reject suggestion -> 200."""
    resp = await _create_suggestion(client)
    suggestion = resp.json()
    sid = suggestion["id"]

    resp = await client.post(f"/api/prompts/rca-test/suggestions/{sid}/reject")
    assert resp.status_code == 200
    assert resp.json()["status"] == "rejected"


# ── GET /api/prompts/{id}/suggestions ─────────────────────────────────


@pytest.mark.asyncio
async def test_list_suggestions_endpoint(client):
    """GET list returns suggestions for the prompt."""
    resp = await _create_suggestion(client)
    assert resp.status_code == 201

    resp = await client.get("/api/prompts/rca-test/suggestions")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["prompt_id"] == "rca-test"


# ── GET /api/ai/status ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ai_status_available(client):
    """GET ai/status with key -> available: true."""
    with patch("backend.routers.suggestions.check_ai_available", return_value=True):
        resp = await client.get("/api/ai/status")
    assert resp.status_code == 200
    assert resp.json()["available"] is True


@pytest.mark.asyncio
async def test_ai_status_unavailable(client):
    """GET ai/status without key -> available: false."""
    with patch("backend.routers.suggestions.check_ai_available", return_value=False):
        resp = await client.get("/api/ai/status")
    assert resp.status_code == 200
    assert resp.json()["available"] is False
