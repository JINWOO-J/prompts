"""Unit tests for ai_service: LLM integration with mocked HTTP responses."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from backend.services import ai_service


@pytest.fixture(autouse=True)
def _set_api_key(monkeypatch):
    """Ensure LLM_API_KEY is set for all tests (unless explicitly cleared)."""
    monkeypatch.setenv("LLM_API_KEY", "test-key-123")
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")


_FAKE_REQUEST = httpx.Request("POST", "https://api.anthropic.com/v1/messages")


def _make_anthropic_response(body: dict) -> httpx.Response:
    """Build a fake Anthropic API response."""
    api_body = {
        "content": [{"type": "text", "text": json.dumps(body)}],
    }
    return httpx.Response(200, json=api_body, request=_FAKE_REQUEST)


def _make_anthropic_raw_response(text: str) -> httpx.Response:
    """Build a fake Anthropic API response with raw text."""
    api_body = {
        "content": [{"type": "text", "text": text}],
    }
    return httpx.Response(200, json=api_body, request=_FAKE_REQUEST)


# ── Happy path ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_suggest_improvement_happy_path():
    """Valid JSON response is parsed correctly."""
    expected = {"improved_content": "Better prompt", "reason": "Clearer wording"}
    response = _make_anthropic_response(expected)

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("backend.services.ai_service.httpx.AsyncClient", return_value=mock_client):
        result = await ai_service.suggest_improvement("Original prompt", "rca")

    assert result["improved_content"] == "Better prompt"
    assert result["reason"] == "Clearer wording"


# ── Timeout ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_suggest_improvement_timeout():
    """httpx.TimeoutException propagates (caller handles it)."""
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("Request timed out"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("backend.services.ai_service.httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(httpx.TimeoutException, match="timed out"):
            await ai_service.suggest_improvement("content", "rca")


# ── Malformed JSON ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_suggest_improvement_malformed_json():
    """Bad JSON with no extractable block -> ValueError after retry."""
    response = _make_anthropic_raw_response("This is not JSON at all")

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("backend.services.ai_service.httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(ValueError, match="Failed to parse LLM response"):
            await ai_service.suggest_improvement("content", "rca")


@pytest.mark.asyncio
async def test_suggest_improvement_malformed_json_retry_succeeds():
    """Bad JSON wrapping but extractable JSON block -> retry succeeds."""
    valid_json = '{"improved_content": "better", "reason": "clarity"}'
    text = f"Here is my suggestion: {valid_json} hope that helps!"
    response = _make_anthropic_raw_response(text)

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("backend.services.ai_service.httpx.AsyncClient", return_value=mock_client):
        result = await ai_service.suggest_improvement("content", "rca")

    assert result["improved_content"] == "better"
    assert result["reason"] == "clarity"


# ── Empty / refusal response ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_suggest_improvement_empty_response():
    """Empty/refusal text -> ValueError."""
    response = _make_anthropic_raw_response("")

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("backend.services.ai_service.httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(ValueError, match="Failed to parse LLM response"):
            await ai_service.suggest_improvement("content", "rca")


# ── Rate limit (429) ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_suggest_improvement_rate_limit_429():
    """429 status -> httpx.HTTPStatusError raised."""
    mock_response = httpx.Response(429, json={"error": "rate limited"}, request=httpx.Request("POST", "https://api.anthropic.com/v1/messages"))

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("backend.services.ai_service.httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(httpx.HTTPStatusError):
            await ai_service.suggest_improvement("content", "rca")


# ── check_ai_available ────────────────────────────────────────────────


def test_check_ai_available_with_key(monkeypatch):
    """LLM_API_KEY set -> True."""
    monkeypatch.setenv("LLM_API_KEY", "some-key")
    assert ai_service.check_ai_available() is True


def test_check_ai_available_without_key(monkeypatch):
    """LLM_API_KEY not set -> False."""
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    assert ai_service.check_ai_available() is False
