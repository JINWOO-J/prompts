"""CRUD 단위 테스트: 생성/조회/수정/삭제, 404/422, 페이지네이션, 필터."""

import os
import tempfile

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.database import init_db, get_db
from backend.routers.prompts import router as prompts_router

import aiosqlite


@pytest_asyncio.fixture
async def app():
    """테스트용 FastAPI 앱 + 임시 DB."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    await init_db(db_path=db_path)

    test_app = FastAPI()
    test_app.include_router(prompts_router)

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
    "content": "# Test\nSample content",
    "tags": ["kubernetes", "pod"],
    "role": "SRE",
}


@pytest.mark.asyncio
async def test_create_get_update_delete(client):
    """생성 → 조회 → 수정 → 삭제 기본 흐름. (Req 3.5, 3.6, 3.7, 3.8)"""
    # 생성
    resp = await client.post("/api/prompts", json=SAMPLE_PROMPT)
    assert resp.status_code == 201
    created = resp.json()
    assert created["title"] == "Test Prompt"
    assert created["category"] == "rca"
    prompt_id = created["id"]

    # 조회
    resp = await client.get(f"/api/prompts/{prompt_id}")
    assert resp.status_code == 200
    assert resp.json()["content"] == "# Test\nSample content"

    # 수정
    resp = await client.put(f"/api/prompts/{prompt_id}", json={"title": "Updated"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"

    # 삭제
    resp = await client.delete(f"/api/prompts/{prompt_id}")
    assert resp.status_code == 204

    # 삭제 후 조회 → 404
    resp = await client.get(f"/api/prompts/{prompt_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_returns_404(client):
    """존재하지 않는 ID → 404. (Req 3.9)"""
    resp = await client.get("/api/prompts/nonexistent-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_nonexistent_returns_404(client):
    resp = await client.put("/api/prompts/nonexistent-id", json={"title": "x"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_returns_404(client):
    resp = await client.delete("/api/prompts/nonexistent-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_missing_fields_returns_422(client):
    """필수 필드 누락 → 422. (Req 3.10)"""
    resp = await client.post("/api/prompts", json={"title": "No content"})
    assert resp.status_code == 422

    resp = await client.post("/api/prompts", json={"content": "No title"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_pagination(client):
    """페이지네이션 동작 확인. (Req 3.1)"""
    for i in range(5):
        await client.post("/api/prompts", json={
            "title": f"Prompt {i}", "category": "rca",
            "content": f"Content {i}", "id": f"rca-p{i}",
        })

    resp = await client.get("/api/prompts", params={"page_size": 2, "page": 1})
    data = resp.json()
    assert data["total"] == 5
    assert len(data["prompts"]) == 2
    assert data["page"] == 1

    resp = await client.get("/api/prompts", params={"page_size": 2, "page": 3})
    assert len(resp.json()["prompts"]) == 1


@pytest.mark.asyncio
async def test_search_q(client):
    """검색어 필터 (q). (Req 3.2)"""
    await client.post("/api/prompts", json={
        "title": "Kubernetes RCA", "category": "rca",
        "content": "Pod crash analysis", "id": "rca-k8s",
    })
    await client.post("/api/prompts", json={
        "title": "AWS Lambda", "category": "application",
        "content": "Lambda timeout", "id": "app-lambda",
    })

    resp = await client.get("/api/prompts", params={"q": "Kubernetes"})
    data = resp.json()
    assert data["total"] == 1
    assert data["prompts"][0]["id"] == "rca-k8s"


@pytest.mark.asyncio
async def test_category_filter(client):
    """카테고리 필터. (Req 3.3)"""
    await client.post("/api/prompts", json={
        "title": "A", "category": "rca", "content": "c", "id": "rca-a",
    })
    await client.post("/api/prompts", json={
        "title": "B", "category": "security", "content": "c", "id": "sec-b",
    })

    resp = await client.get("/api/prompts", params={"category": "security"})
    data = resp.json()
    assert data["total"] == 1
    assert data["prompts"][0]["category"] == "security"


@pytest.mark.asyncio
async def test_tag_filter(client):
    """태그 필터. (Req 3.4)"""
    await client.post("/api/prompts", json={
        "title": "A", "category": "rca", "content": "c",
        "tags": ["kubernetes", "pod"], "id": "rca-a",
    })
    await client.post("/api/prompts", json={
        "title": "B", "category": "rca", "content": "c",
        "tags": ["lambda"], "id": "rca-b",
    })

    resp = await client.get("/api/prompts", params={"tag": "kubernetes"})
    data = resp.json()
    assert data["total"] == 1
    assert data["prompts"][0]["id"] == "rca-a"
