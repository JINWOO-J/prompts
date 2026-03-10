"""속성 기반 테스트: CRUD 라운드트립, 검색 필터, 페이지네이션, 유효하지 않은 요청."""

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

CATEGORIES = ["rca", "incident-response", "application", "infrastructure",
              "security", "data-ai", "shared", "techniques"]


def _make_app(db_path: str) -> FastAPI:
    """테스트용 FastAPI 앱을 생성한다."""
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
    return test_app


# ---------------------------------------------------------------------------
# Feature: prompt-management-app, Property 2: CRUD 라운드트립
# **Validates: Requirements 3.5, 3.6**
# ---------------------------------------------------------------------------

# 유효한 프롬프트 데이터 생성 전략
_printable_text = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P", "Z"), blacklist_characters="\x00"),
    min_size=1, max_size=80,
)
_tag_strategy = st.lists(
    st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789-", min_size=1, max_size=20),
    min_size=0, max_size=5,
)

_prompt_strategy = st.fixed_dictionaries({
    "title": _printable_text,
    "category": st.sampled_from(CATEGORIES),
    "content": _printable_text,
    "tags": _tag_strategy,
    "role": st.text(min_size=0, max_size=20),
})


@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(data=_prompt_strategy)
@pytest.mark.asyncio
async def test_crud_roundtrip(data):
    """POST로 생성한 프롬프트를 GET으로 조회하면 동일한 필드가 반환되어야 한다."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        await init_db(db_path=db_path)
        app = _make_app(db_path)

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post("/api/prompts", json=data)
            assert resp.status_code == 201
            created = resp.json()

            resp = await client.get(f"/api/prompts/{created['id']}")
            assert resp.status_code == 200
            fetched = resp.json()

            assert fetched["title"] == data["title"]
            assert fetched["category"] == data["category"]
            assert fetched["content"] == data["content"]
            assert fetched["tags"] == data["tags"]
            assert fetched["role"] == data["role"]
    finally:
        os.unlink(db_path)


# ---------------------------------------------------------------------------
# Feature: prompt-management-app, Property 3: 검색 필터 정확성
# **Validates: Requirements 3.2, 3.3, 3.4**
# ---------------------------------------------------------------------------

_search_term = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz", min_size=2, max_size=10,
)


@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    prompts=st.lists(_prompt_strategy, min_size=1, max_size=10),
    search_term=_search_term,
)
@pytest.mark.asyncio
async def test_search_filter_correctness(prompts, search_term):
    """검색/카테고리/태그 필터 결과는 모두 해당 조건을 만족해야 한다."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        await init_db(db_path=db_path)
        app = _make_app(db_path)

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            # 프롬프트 삽입 (ID 충돌 방지를 위해 명시적 ID)
            for i, p in enumerate(prompts):
                payload = {**p, "id": f"test-{i}"}
                await client.post("/api/prompts", json=payload)

            # q 검색: 결과의 title 또는 content에 검색어 포함
            resp = await client.get("/api/prompts", params={"q": search_term, "page_size": 200})
            for item in resp.json()["prompts"]:
                detail = await client.get(f"/api/prompts/{item['id']}")
                d = detail.json()
                assert (
                    search_term.lower() in d["title"].lower()
                    or search_term.lower() in d["content"].lower()
                ), f"검색어 '{search_term}'가 title/content에 없음: {d['title']}"

            # 카테고리 필터
            cat = prompts[0]["category"]
            resp = await client.get("/api/prompts", params={"category": cat, "page_size": 200})
            for item in resp.json()["prompts"]:
                assert item["category"] == cat

            # 태그 필터 (첫 프롬프트에 태그가 있을 때만)
            if prompts[0]["tags"]:
                tag = prompts[0]["tags"][0]
                resp = await client.get("/api/prompts", params={"tag": tag, "page_size": 200})
                for item in resp.json()["prompts"]:
                    assert tag in item["tags"], f"태그 '{tag}'가 결과에 없음"
    finally:
        os.unlink(db_path)


# ---------------------------------------------------------------------------
# Feature: prompt-management-app, Property 4: 페이지네이션 일관성
# **Validates: Requirements 3.1**
# ---------------------------------------------------------------------------


@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    count=st.integers(min_value=1, max_value=30),
    page_size=st.integers(min_value=1, max_value=10),
)
@pytest.mark.asyncio
async def test_pagination_consistency(count, page_size):
    """모든 페이지를 순회하면 전체 ID 집합과 동일하고 중복이 없어야 한다."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        await init_db(db_path=db_path)
        app = _make_app(db_path)

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            expected_ids = set()
            for i in range(count):
                pid = f"rca-page-{i}"
                expected_ids.add(pid)
                await client.post("/api/prompts", json={
                    "title": f"P{i}", "category": "rca",
                    "content": f"C{i}", "id": pid,
                })

            # 모든 페이지 순회
            collected_ids: list[str] = []
            page = 1
            while True:
                resp = await client.get("/api/prompts", params={
                    "page": page, "page_size": page_size,
                })
                data = resp.json()
                items = data["prompts"]
                if not items:
                    break
                collected_ids.extend(item["id"] for item in items)
                page += 1

            assert set(collected_ids) == expected_ids, "ID 집합 불일치"
            assert len(collected_ids) == len(set(collected_ids)), "중복 ID 존재"
    finally:
        os.unlink(db_path)


# ---------------------------------------------------------------------------
# Feature: prompt-management-app, Property 8: 유효하지 않은 요청 거부
# **Validates: Requirements 3.9, 3.10**
# ---------------------------------------------------------------------------


@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    random_id=st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789-",
        min_size=5, max_size=30,
    ),
)
@pytest.mark.asyncio
async def test_invalid_request_rejection(random_id):
    """비존재 ID → 404, 필수 필드 누락 → 422."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        await init_db(db_path=db_path)
        app = _make_app(db_path)

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            # 비존재 ID → 404
            assert (await client.get(f"/api/prompts/{random_id}")).status_code == 404
            assert (await client.put(f"/api/prompts/{random_id}", json={"title": "x"})).status_code == 404
            assert (await client.delete(f"/api/prompts/{random_id}")).status_code == 404

            # 필수 필드 누락 → 422
            assert (await client.post("/api/prompts", json={"title": "no content"})).status_code == 422
            assert (await client.post("/api/prompts", json={"content": "no title"})).status_code == 422
            assert (await client.post("/api/prompts", json={})).status_code == 422
    finally:
        os.unlink(db_path)
