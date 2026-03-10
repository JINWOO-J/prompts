"""전체 통합 테스트: 마이그레이션 → API CRUD → 버전 관리 → 익스포트 → 동기화 흐름 검증."""

import json

import httpx
import pytest
import pytest_asyncio
import yaml
from fastapi import FastAPI

import aiosqlite

from backend.database import init_db, get_db
from backend.migrate import migrate_all
from backend.routers.prompts import router as prompts_router
from backend.routers.versions import router as versions_router
from backend.routers.export import router as export_router


@pytest_asyncio.fixture
async def setup(tmp_path):
    """임시 DB + 샘플 .md 파일 + FastAPI 앱을 준비한다."""
    db_path = str(tmp_path / "test.db")
    await init_db(db_path=db_path)

    # 샘플 .md 파일 생성
    rca_dir = tmp_path / "md_source" / "rca"
    rca_dir.mkdir(parents=True)
    (rca_dir / "basic_rca.md").write_text(
        "---\ncategory: rca\ntags:\n- kubernetes\n- pod\nrole: SRE\norigin: custom\nsource: ''\n---\n# Basic RCA\nRoot cause analysis content",
        encoding="utf-8",
    )
    (rca_dir / "advanced_rca.md").write_text(
        "---\ncategory: rca\ntags:\n- aws\nrole: DevOps\norigin: custom\nsource: ''\n---\n# Advanced RCA\nAdvanced analysis content",
        encoding="utf-8",
    )

    sec_dir = tmp_path / "md_source" / "security"
    sec_dir.mkdir(parents=True)
    (sec_dir / "iam_audit.md").write_text(
        "---\ncategory: security\ntags:\n- iam\n- aws\nrole: Security\norigin: custom\nsource: ''\n---\n# IAM Audit\nIAM audit content",
        encoding="utf-8",
    )

    test_app = FastAPI()
    test_app.include_router(prompts_router)
    test_app.include_router(versions_router)
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

    return {
        "app": test_app,
        "db_path": db_path,
        "md_source": tmp_path / "md_source",
        "tmp_path": tmp_path,
        "get_db": override_get_db,
    }


@pytest.mark.asyncio
async def test_full_flow(setup):
    """마이그레이션 → CRUD → 버전 관리 → 익스포트 → 동기화 전체 흐름."""
    app = setup["app"]
    db_path = setup["db_path"]
    md_source = setup["md_source"]
    tmp_path = setup["tmp_path"]

    # ── 1. 마이그레이션: .md 파일 → DB ──
    summary = await migrate_all(
        db_path=db_path,
        root=md_source,
        categories=["rca", "security"],
    )
    assert summary.scanned == 3
    assert summary.imported == 3
    assert summary.skipped == 0

    # 중복 마이그레이션 → 전부 스킵
    summary2 = await migrate_all(
        db_path=db_path,
        root=md_source,
        categories=["rca", "security"],
    )
    assert summary2.imported == 0
    assert summary2.skipped == 3

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:

        # ── 2. API로 마이그레이션된 프롬프트 조회 ──
        resp = await client.get("/api/prompts")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3

        # 카테고리 필터
        resp = await client.get("/api/prompts", params={"category": "security"})
        assert resp.json()["total"] == 1

        # ── 3. 새 프롬프트 생성 ──
        new_prompt = {
            "title": "Integration Test Prompt",
            "category": "application",
            "content": "# Integration\nTest content here",
            "tags": ["test", "integration"],
            "role": "Tester",
        }
        resp = await client.post("/api/prompts", json=new_prompt)
        assert resp.status_code == 201
        created = resp.json()
        prompt_id = created["id"]
        assert created["title"] == "Integration Test Prompt"

        # 전체 개수 확인
        resp = await client.get("/api/prompts")
        assert resp.json()["total"] == 4

        # ── 4. 프롬프트 수정 → 버전 자동 생성 ──
        resp = await client.put(
            f"/api/prompts/{prompt_id}",
            json={"title": "Updated Title", "content": "# Updated\nNew content"},
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated Title"

        # 버전 확인
        resp = await client.get(f"/api/prompts/{prompt_id}/versions")
        assert resp.status_code == 200
        versions = resp.json()
        assert len(versions) == 1
        assert versions[0]["title"] == "Integration Test Prompt"
        assert versions[0]["version_number"] == 1

        # 두 번째 수정
        resp = await client.put(
            f"/api/prompts/{prompt_id}",
            json={"content": "# Final\nFinal content"},
        )
        assert resp.status_code == 200

        resp = await client.get(f"/api/prompts/{prompt_id}/versions")
        versions = resp.json()
        assert len(versions) == 2
        assert versions[0]["version_number"] == 2

        # ── 5. 버전 복원 ──
        resp = await client.post(f"/api/prompts/{prompt_id}/versions/1/restore")
        assert resp.status_code == 200
        restored = resp.json()
        assert restored["title"] == "Integration Test Prompt"
        assert restored["content"] == "# Integration\nTest content here"

        # 복원 후 버전 수 증가 확인
        resp = await client.get(f"/api/prompts/{prompt_id}/versions")
        assert len(resp.json()) == 3

        # ── 6. 프롬프트 삭제 → 연쇄 제거 ──
        resp = await client.delete(f"/api/prompts/{prompt_id}")
        assert resp.status_code == 204

        resp = await client.get(f"/api/prompts/{prompt_id}")
        assert resp.status_code == 404

        # 버전도 삭제 확인
        resp = await client.get(f"/api/prompts/{prompt_id}/versions")
        assert resp.status_code == 404

        # 남은 프롬프트 3개 (마이그레이션된 것만)
        resp = await client.get("/api/prompts")
        assert resp.json()["total"] == 3

        # ── 7. 익스포트: DB → .md 파일 ──
        from backend.services.export_service import export_all_to_md

        export_dir = tmp_path / "export_out"
        async for db in setup["get_db"]():
            export_summary = await export_all_to_md(db, str(export_dir))
            break

        assert export_summary.total_exported == 3
        # 카테고리 디렉토리에 파일 존재 확인
        assert (export_dir / "rca").exists()
        assert (export_dir / "security").exists()

        exported_files = list(export_dir.rglob("*.md"))
        assert len(exported_files) == 3

        # 익스포트된 파일에 frontmatter 포함 확인
        sample = next(f for f in exported_files if "basic_rca" in f.name)
        content = sample.read_text(encoding="utf-8")
        assert content.startswith("---")
        assert "rca" in content

        # ── 8. 동기화: meta.yaml + data.json 재생성 ──
        from backend.services.export_service import sync_meta_files

        sync_root = tmp_path / "sync_out"
        (sync_root / "web").mkdir(parents=True)

        async for db in setup["get_db"]():
            sync_summary = await sync_meta_files(db, str(sync_root))
            break

        assert sync_summary.total_exported == 3

        meta_path = sync_root / "prompts.meta.yaml"
        assert meta_path.exists()
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
        assert meta["_meta"]["total"] == 3
        assert len(meta["prompts"]) == 3

        data_path = sync_root / "web" / "data.json"
        assert data_path.exists()
        data_json = json.loads(data_path.read_text(encoding="utf-8"))
        assert data_json["_meta"]["total"] == 3
        assert all("content" in p for p in data_json["prompts"])
