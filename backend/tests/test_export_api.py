"""익스포트 단위 테스트: .md 파일 생성, meta.yaml/data.json 재생성 확인 (Req 5.1~5.5)."""

import json
import os
import tempfile

import httpx
import pytest
import pytest_asyncio
import yaml
from fastapi import FastAPI

import aiosqlite

from backend.database import init_db, get_db
from backend.models import PromptResponse
from backend.routers.prompts import router as prompts_router
from backend.routers.export import router as export_router
from backend.services.export_service import format_prompt_as_md, parse_md_file


@pytest_asyncio.fixture
async def app(tmp_path):
    """테스트용 FastAPI 앱 + 임시 DB."""
    db_path = str(tmp_path / "test.db")
    await init_db(db_path=db_path)

    test_app = FastAPI()
    test_app.include_router(prompts_router)
    test_app.include_router(export_router)

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


@pytest_asyncio.fixture
async def client(app):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


SAMPLE = {
    "id": "rca-test-prompt",
    "title": "Test Prompt",
    "category": "rca",
    "content": "# Test\nSample content",
    "tags": ["kubernetes", "pod"],
    "role": "SRE",
}


def test_format_prompt_as_md():
    """format_prompt_as_md가 올바른 YAML frontmatter + body를 생성한다. (Req 5.2)"""
    prompt = PromptResponse(
        id="rca-test", title="Test", category="rca",
        content="# Hello\nWorld", tags=["k8s"], role="SRE",
        origin="custom", source="", file_path="rca/test.md",
        created_at="2024-01-01", updated_at="2024-01-01",
    )
    md = format_prompt_as_md(prompt)

    assert md.startswith("---\n")
    # frontmatter 파싱
    end = md.find("---", 3)
    fm = yaml.safe_load(md[3:end])
    assert fm["category"] == "rca"
    assert fm["tags"] == ["k8s"]
    assert fm["role"] == "SRE"

    # body
    body = md[end + 3:].lstrip("\n")
    assert body.startswith("# Hello")


def test_parse_md_file(tmp_path):
    """parse_md_file이 .md 파일을 PromptCreate로 변환한다."""
    md_content = "---\ncategory: security\ntags:\n- aws\nrole: DevOps\n---\n# Security Guide\nContent here"
    f = tmp_path / "test.md"
    f.write_text(md_content, encoding="utf-8")

    result = parse_md_file(f)
    assert result.category == "security"
    assert result.tags == ["aws"]
    assert result.role == "DevOps"
    assert "Security Guide" in result.content


def test_format_parse_roundtrip(tmp_path):
    """format → write → parse 라운드트립에서 핵심 필드가 보존된다."""
    prompt = PromptResponse(
        id="app-roundtrip", title="Roundtrip", category="application",
        content="# RT\nBody text", tags=["lambda", "timeout"], role="Dev",
        origin="custom", source="https://example.com",
        file_path="application/roundtrip.md",
        created_at="2024-01-01", updated_at="2024-01-01",
    )
    md = format_prompt_as_md(prompt)
    f = tmp_path / "roundtrip.md"
    f.write_text(md, encoding="utf-8")

    parsed = parse_md_file(f)
    assert parsed.category == prompt.category
    assert parsed.tags == prompt.tags
    assert parsed.role == prompt.role
    assert parsed.content.strip() == prompt.content.strip()


@pytest.mark.asyncio
async def test_export_creates_md_files(client, tmp_path):
    """GET /api/export가 .md 파일을 생성하고 ExportSummary를 반환한다. (Req 5.1, 5.3, 5.4)"""
    # 프롬프트 생성
    await client.post("/api/prompts", json=SAMPLE)

    # export_all_to_md를 직접 호출 (라우터는 PROJECT_ROOT를 사용하므로 서비스 직접 테스트)
    from backend.services.export_service import export_all_to_md

    db_path = None
    # app fixture에서 DB 경로 추출
    async for db in client._transport.app.dependency_overrides[get_db]():
        summary = await export_all_to_md(db, str(tmp_path))
        break

    assert summary.total_exported == 1
    # 카테고리 디렉토리에 파일이 생성되었는지 확인
    exported = tmp_path / "rca" / "rca-test-prompt.md"
    assert exported.exists()

    content = exported.read_text(encoding="utf-8")
    assert "---" in content
    assert "# Test" in content


@pytest.mark.asyncio
async def test_sync_regenerates_meta_files(client, tmp_path):
    """POST /api/export/sync가 meta.yaml과 data.json을 재생성한다. (Req 5.5)"""
    await client.post("/api/prompts", json=SAMPLE)

    from backend.services.export_service import sync_meta_files

    # web 디렉토리 생성
    (tmp_path / "web").mkdir(exist_ok=True)

    async for db in client._transport.app.dependency_overrides[get_db]():
        summary = await sync_meta_files(db, str(tmp_path))
        break

    assert summary.total_exported == 1

    # meta.yaml 확인
    meta_path = tmp_path / "prompts.meta.yaml"
    assert meta_path.exists()
    meta = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
    assert meta["_meta"]["total"] == 1
    assert len(meta["prompts"]) == 1
    assert meta["prompts"][0]["id"] == "rca-test-prompt"

    # data.json 확인
    data_path = tmp_path / "web" / "data.json"
    assert data_path.exists()
    data = json.loads(data_path.read_text(encoding="utf-8"))
    assert data["_meta"]["total"] == 1
    assert "content" in data["prompts"][0]  # data.json은 content 포함
