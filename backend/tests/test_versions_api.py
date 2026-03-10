"""버전 관리 단위 테스트: 업데이트 시 버전 생성, 버전 목록 정렬, 복원 동작 (Req 4.1~4.6)."""

import os
import tempfile

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

import aiosqlite

from backend.database import init_db, get_db
from backend.routers.prompts import router as prompts_router
from backend.routers.versions import router as versions_router


@pytest_asyncio.fixture
async def app():
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    await init_db(db_path=db_path)

    test_app = FastAPI()
    test_app.include_router(prompts_router)
    test_app.include_router(versions_router)

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


SAMPLE = {
    "title": "Original Title",
    "category": "rca",
    "content": "# Original\nContent here",
    "tags": ["k8s"],
    "role": "SRE",
    "id": "rca-original",
}


@pytest.mark.asyncio
async def test_update_creates_version(client):
    """PUT 업데이트 시 이전 상태가 버전으로 저장된다. (Req 4.1)"""
    await client.post("/api/prompts", json=SAMPLE)

    await client.put("/api/prompts/rca-original", json={"title": "Updated Title"})

    resp = await client.get("/api/prompts/rca-original/versions")
    assert resp.status_code == 200
    versions = resp.json()
    assert len(versions) == 1
    assert versions[0]["title"] == "Original Title"
    assert versions[0]["content"] == "# Original\nContent here"
    assert versions[0]["version_number"] == 1


@pytest.mark.asyncio
async def test_version_number_increments(client):
    """연속 업데이트 시 version_number가 단조 증가한다. (Req 4.2)"""
    await client.post("/api/prompts", json=SAMPLE)

    await client.put("/api/prompts/rca-original", json={"title": "V2"})
    await client.put("/api/prompts/rca-original", json={"title": "V3"})
    await client.put("/api/prompts/rca-original", json={"title": "V4"})

    resp = await client.get("/api/prompts/rca-original/versions")
    versions = resp.json()
    assert len(versions) == 3
    # 내림차순 정렬
    numbers = [v["version_number"] for v in versions]
    assert numbers == [3, 2, 1]


@pytest.mark.asyncio
async def test_versions_ordered_descending(client):
    """버전 목록은 version_number 내림차순이다. (Req 4.3)"""
    await client.post("/api/prompts", json=SAMPLE)
    await client.put("/api/prompts/rca-original", json={"content": "c1"})
    await client.put("/api/prompts/rca-original", json={"content": "c2"})

    resp = await client.get("/api/prompts/rca-original/versions")
    versions = resp.json()
    numbers = [v["version_number"] for v in versions]
    assert numbers == sorted(numbers, reverse=True)


@pytest.mark.asyncio
async def test_get_specific_version(client):
    """특정 버전 번호로 조회할 수 있다. (Req 4.4)"""
    await client.post("/api/prompts", json=SAMPLE)
    await client.put("/api/prompts/rca-original", json={"title": "After Update"})

    resp = await client.get("/api/prompts/rca-original/versions/1")
    assert resp.status_code == 200
    version = resp.json()
    assert version["version_number"] == 1
    assert version["title"] == "Original Title"


@pytest.mark.asyncio
async def test_get_nonexistent_version_404(client):
    """존재하지 않는 버전 번호 → 404. (Req 4.6)"""
    await client.post("/api/prompts", json=SAMPLE)

    resp = await client.get("/api/prompts/rca-original/versions/999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_restore_version(client):
    """버전 복원 시 프롬프트 내용이 해당 버전으로 돌아간다. (Req 4.5)"""
    await client.post("/api/prompts", json=SAMPLE)
    await client.put("/api/prompts/rca-original", json={
        "title": "Changed", "content": "New content",
    })

    # v1 = 원본 상태
    resp = await client.post("/api/prompts/rca-original/versions/1/restore")
    assert resp.status_code == 200
    restored = resp.json()
    assert restored["title"] == "Original Title"
    assert restored["content"] == "# Original\nContent here"


@pytest.mark.asyncio
async def test_restore_creates_new_version(client):
    """복원 행위 자체가 새 버전을 생성한다. (Req 4.5)"""
    await client.post("/api/prompts", json=SAMPLE)
    await client.put("/api/prompts/rca-original", json={"title": "Changed"})
    # 현재 버전: 1개 (원본 → Changed 업데이트 시 생성)

    await client.post("/api/prompts/rca-original/versions/1/restore")
    # 복원 시 "Changed" 상태가 새 버전으로 저장됨

    resp = await client.get("/api/prompts/rca-original/versions")
    versions = resp.json()
    assert len(versions) == 2
    assert versions[0]["version_number"] == 2
    assert "restore" in versions[0]["change_summary"].lower()


@pytest.mark.asyncio
async def test_restore_nonexistent_version_404(client):
    """존재하지 않는 버전 복원 → 404. (Req 4.6)"""
    await client.post("/api/prompts", json=SAMPLE)

    resp = await client.post("/api/prompts/rca-original/versions/999/restore")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_versions_for_nonexistent_prompt_404(client):
    """존재하지 않는 프롬프트의 버전 목록 → 404."""
    resp = await client.get("/api/prompts/nonexistent/versions")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_refreshes_updated_at(client):
    """업데이트 시 updated_at이 갱신된다. (Req 3.7)"""
    resp = await client.post("/api/prompts", json=SAMPLE)
    original_updated = resp.json()["updated_at"]

    resp = await client.put("/api/prompts/rca-original", json={"title": "New"})
    new_updated = resp.json()["updated_at"]
    assert new_updated >= original_updated
