"""속성 기반 테스트: 버전 자동 생성, 복원 라운드트립, 삭제 연쇄 제거."""

import os
import tempfile

import aiosqlite
import httpx
import pytest
from fastapi import FastAPI
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from backend.database import init_db, get_db
from backend.routers.prompts import router as prompts_router
from backend.routers.versions import router as versions_router

CATEGORIES = [
    "rca", "incident-response", "application", "infrastructure",
    "security", "data-ai", "shared", "techniques",
]


def _make_app(db_path: str) -> FastAPI:
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
    return test_app


_printable = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P", "Z"), blacklist_characters="\x00"),
    min_size=1, max_size=60,
)
_tag_strategy = st.lists(
    st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789-", min_size=1, max_size=15),
    min_size=0, max_size=4,
)


# ---------------------------------------------------------------------------
# Feature: prompt-management-app, Property 5: 업데이트 시 버전 자동 생성
# **Validates: Requirements 3.7, 4.1, 4.2**
# ---------------------------------------------------------------------------

_update_strategy = st.fixed_dictionaries({
    "title": _printable,
    "content": _printable,
    "tags": _tag_strategy,
})


@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    initial_cat=st.sampled_from(CATEGORIES),
    initial_title=_printable,
    initial_content=_printable,
    updates=st.lists(_update_strategy, min_size=1, max_size=5),
)
@pytest.mark.asyncio
async def test_update_creates_version(initial_cat, initial_title, initial_content, updates):
    """업데이트마다 이전 상태가 버전으로 저장되고, version_number가 단조 증가하며, updated_at이 갱신된다."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        await init_db(db_path=db_path)
        app = _make_app(db_path)

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            # 프롬프트 생성
            create_resp = await client.post("/api/prompts", json={
                "title": initial_title, "category": initial_cat,
                "content": initial_content, "id": "test-ver-prop5",
            })
            assert create_resp.status_code == 201
            prev_updated = create_resp.json()["updated_at"]

            # 연속 업데이트
            for i, upd in enumerate(updates):
                # 업데이트 전 현재 상태 기억
                before = await client.get("/api/prompts/test-ver-prop5")
                before_data = before.json()

                resp = await client.put("/api/prompts/test-ver-prop5", json=upd)
                assert resp.status_code == 200

                # (2) updated_at 갱신 확인
                new_updated = resp.json()["updated_at"]
                assert new_updated >= prev_updated
                prev_updated = new_updated

                # (1) 버전에 업데이트 전 상태가 저장되었는지 확인
                ver_resp = await client.get(f"/api/prompts/test-ver-prop5/versions/{i + 1}")
                assert ver_resp.status_code == 200
                ver = ver_resp.json()
                assert ver["title"] == before_data["title"]
                assert ver["content"] == before_data["content"]

            # (3) version_number 단조 증가 확인
            all_vers = await client.get("/api/prompts/test-ver-prop5/versions")
            numbers = [v["version_number"] for v in all_vers.json()]
            assert numbers == sorted(numbers, reverse=True)  # 내림차순 정렬
            assert len(numbers) == len(updates)
            assert numbers == list(range(len(updates), 0, -1))
    finally:
        os.unlink(db_path)


# ---------------------------------------------------------------------------
# Feature: prompt-management-app, Property 6: 버전 복원 라운드트립
# **Validates: Requirements 4.4, 4.5**
# ---------------------------------------------------------------------------


@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    updates=st.lists(_update_strategy, min_size=2, max_size=5),
    restore_idx=st.integers(min_value=0, max_value=100),
)
@pytest.mark.asyncio
async def test_version_restore_roundtrip(updates, restore_idx):
    """임의 버전으로 복원하면 (1) 프롬프트 내용이 해당 버전과 동일하고 (2) 복원 자체가 새 버전을 생성한다."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        await init_db(db_path=db_path)
        app = _make_app(db_path)

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            # 프롬프트 생성 + 여러 번 업데이트
            await client.post("/api/prompts", json={
                "title": "Init", "category": "rca",
                "content": "Init content", "id": "test-ver-prop6",
            })
            for upd in updates:
                await client.put("/api/prompts/test-ver-prop6", json=upd)

            # 복원할 버전 선택 (1 ~ len(updates) 범위)
            version_to_restore = (restore_idx % len(updates)) + 1

            # 복원 전 버전 수
            before_versions = await client.get("/api/prompts/test-ver-prop6/versions")
            count_before = len(before_versions.json())

            # 복원할 버전의 내용 조회
            target_ver = await client.get(
                f"/api/prompts/test-ver-prop6/versions/{version_to_restore}"
            )
            target_data = target_ver.json()

            # 복원 실행
            restore_resp = await client.post(
                f"/api/prompts/test-ver-prop6/versions/{version_to_restore}/restore"
            )
            assert restore_resp.status_code == 200
            restored = restore_resp.json()

            # (1) 프롬프트 내용이 해당 버전과 동일
            assert restored["title"] == target_data["title"]
            assert restored["content"] == target_data["content"]
            assert restored["tags"] == target_data["tags"]

            # (2) 복원 자체가 새 버전을 생성
            after_versions = await client.get("/api/prompts/test-ver-prop6/versions")
            count_after = len(after_versions.json())
            assert count_after == count_before + 1
    finally:
        os.unlink(db_path)


# ---------------------------------------------------------------------------
# Feature: prompt-management-app, Property 7: 삭제 연쇄 제거
# **Validates: Requirements 3.8**
# ---------------------------------------------------------------------------


@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    update_count=st.integers(min_value=1, max_value=5),
)
@pytest.mark.asyncio
async def test_delete_cascades_to_versions(update_count):
    """버전이 있는 프롬프트를 삭제하면 프롬프트와 모든 버전이 DB에서 제거된다."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        await init_db(db_path=db_path)
        app = _make_app(db_path)

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            # 프롬프트 생성 + 업데이트로 버전 생성
            await client.post("/api/prompts", json={
                "title": "To Delete", "category": "rca",
                "content": "Will be deleted", "id": "test-ver-prop7",
            })
            for i in range(update_count):
                await client.put("/api/prompts/test-ver-prop7", json={
                    "title": f"Update {i}",
                })

            # 버전이 존재하는지 확인
            ver_resp = await client.get("/api/prompts/test-ver-prop7/versions")
            assert len(ver_resp.json()) == update_count

            # 삭제
            del_resp = await client.delete("/api/prompts/test-ver-prop7")
            assert del_resp.status_code == 204

            # 프롬프트 조회 → 404
            assert (await client.get("/api/prompts/test-ver-prop7")).status_code == 404

            # DB에서 직접 버전 확인
            async with aiosqlite.connect(db_path) as db:
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM versions WHERE prompt_id = ?",
                    ("test-ver-prop7",),
                )
                row = await cursor.fetchone()
                assert row[0] == 0, "삭제 후 버전이 남아있음"
    finally:
        os.unlink(db_path)
