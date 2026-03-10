"""속성 기반 테스트: 익스포트 파일 경로 정확성 (Property 12).

테스트 프레임워크: hypothesis
"""

import json
import os
import tempfile
from pathlib import Path

import aiosqlite
import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from backend.database import init_db
from backend.services.export_service import CATEGORIES, export_all_to_md


# ---------------------------------------------------------------------------
# 전략(Strategy)
# ---------------------------------------------------------------------------

category_strategy = st.sampled_from(CATEGORIES)

safe_text = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N"), whitelist_characters="-_ "),
    min_size=1,
    max_size=30,
).filter(lambda s: s.strip())

tag_strategy = st.lists(
    safe_text.map(lambda s: s.strip()[:15]),
    min_size=0,
    max_size=3,
).map(lambda tags: [t for t in tags if t])


# ---------------------------------------------------------------------------
# Property 12: 익스포트 파일 경로 정확성
# Feature: prompt-management-app, Property 12: 익스포트 파일 경로 정확성
# ---------------------------------------------------------------------------

@given(
    category=category_strategy,
    title=safe_text,
    body=safe_text,
    tags=tag_strategy,
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.asyncio
async def test_export_file_path_matches_category(category, title, body, tags):
    """**Validates: Requirements 5.3**

    임의의 카테고리를 가진 프롬프트를 DB에 삽입 후 익스포트하면,
    생성된 .md 파일은 해당 카테고리 디렉토리 안에 위치해야 한다.
    """
    fd_db, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd_db)
    output_dir = tempfile.mkdtemp()

    try:
        await init_db(db_path=db_path)

        prompt_id = f"{category[:3]}-test-export"
        now = "2024-01-01T00:00:00+00:00"

        async with aiosqlite.connect(db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            db.row_factory = aiosqlite.Row

            await db.execute(
                """INSERT INTO prompts
                   (id, title, category, content, tags, role, origin, source, file_path, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, '', '', '', ?, ?, ?)""",
                (
                    prompt_id, title.strip(), category, body,
                    json.dumps(tags, ensure_ascii=False),
                    f"{category}/{prompt_id}.md",
                    now, now,
                ),
            )
            await db.commit()

            summary = await export_all_to_md(db, output_dir)

        assert summary.total_exported == 1

        # 핵심 속성: 익스포트된 파일이 카테고리 디렉토리에 위치해야 한다
        cat_dir = Path(output_dir) / category
        assert cat_dir.exists(), f"카테고리 디렉토리 {category}가 존재하지 않음"

        exported_files = list(cat_dir.glob("*.md"))
        assert len(exported_files) == 1, f"카테고리 디렉토리에 .md 파일이 1개여야 함, 실제: {len(exported_files)}"

        # 파일 경로의 부모 디렉토리가 카테고리와 일치
        assert exported_files[0].parent.name == category

    finally:
        os.unlink(db_path)
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)
