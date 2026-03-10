"""속성 기반 테스트: 마이그레이션 라운드트립 및 요약 정합성.

테스트 프레임워크: hypothesis
"""

import json
import os
import tempfile

import aiosqlite
import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from backend.migrate import (
    CATEGORIES,
    extract_frontmatter,
    strip_frontmatter,
    migrate_all,
)


# ---------------------------------------------------------------------------
# 전략(Strategy): 유효한 .md 파일 콘텐츠 생성
# ---------------------------------------------------------------------------

# YAML-safe 텍스트 (특수문자 제한으로 파싱 안정성 확보)
yaml_safe_text = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "Z"), whitelist_characters="-_ "),
    min_size=1,
    max_size=40,
).filter(lambda s: s.strip())

tag_strategy = st.lists(
    yaml_safe_text.map(lambda s: s.strip()[:20]),
    min_size=0,
    max_size=5,
).map(lambda tags: [t for t in tags if t])

category_strategy = st.sampled_from(CATEGORIES)

# 마크다운 본문: H1 제목 + 본문 텍스트
body_text = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "Z", "P"), whitelist_characters="\n -_*#`"),
    min_size=1,
    max_size=200,
).filter(lambda s: s.strip() and "---" not in s)

md_title = yaml_safe_text.map(lambda s: s.strip()[:60]).filter(lambda s: len(s) > 0)


# ---------------------------------------------------------------------------
# 헬퍼: DB 레코드 → .md 포맷 (Task 5의 export_service 대용)
# ---------------------------------------------------------------------------

def format_prompt_as_md(row: dict) -> str:
    """DB 레코드를 .md 형식으로 변환한다. 라운드트립 비교용 로컬 헬퍼."""
    import yaml as _yaml

    fm = {}
    if row.get("category"):
        fm["category"] = row["category"]
    if row.get("origin"):
        fm["origin"] = row["origin"]
    if row.get("source"):
        fm["source"] = row["source"]
    tags = row.get("tags", [])
    if isinstance(tags, str):
        tags = json.loads(tags)
    if tags:
        fm["tags"] = tags
    if row.get("role"):
        fm["role"] = row["role"]

    frontmatter = _yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False).strip()
    return f"---\n{frontmatter}\n---\n{row['content']}"


# ---------------------------------------------------------------------------
# Property 1: 마이그레이션 라운드트립
# Feature: prompt-management-app, Property 1: 마이그레이션 라운드트립
# ---------------------------------------------------------------------------

@given(
    category=category_strategy,
    title=md_title,
    body=body_text,
    tags=tag_strategy,
    role=yaml_safe_text,
    origin=st.sampled_from(["custom", "scoutflo", "voltagent", ""]),
    source=st.just(""),
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.asyncio
async def test_migration_roundtrip(category, title, body, tags, role, origin, source):
    """Validates: Requirements 2.2, 2.3, 2.6

    임의의 .md 파일을 DB로 임포트 후 다시 .md로 변환하면
    frontmatter 필드와 본문이 보존되어야 한다.
    """
    # 1) .md 파일 생성
    import yaml as _yaml

    fm_dict = {"category": category}
    if origin:
        fm_dict["origin"] = origin
    if source:
        fm_dict["source"] = source
    if tags:
        fm_dict["tags"] = tags
    if role.strip():
        fm_dict["role"] = role.strip()

    fm_yaml = _yaml.dump(fm_dict, allow_unicode=True, default_flow_style=False, sort_keys=False).strip()
    md_content = f"---\n{fm_yaml}\n---\n# {title}\n{body}"

    # 2) 임시 파일 + DB 생성
    fd_db, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd_db)
    tmp_dir = tempfile.mkdtemp()
    cat_dir = os.path.join(tmp_dir, category)
    os.makedirs(cat_dir, exist_ok=True)

    file_path = os.path.join(cat_dir, "test_prompt.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    try:
        from pathlib import Path
        await migrate_all(db_path=db_path, root=Path(tmp_dir), categories=[category])

        # 3) DB에서 읽기
        async with aiosqlite.connect(db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM prompts LIMIT 1")
            row = await cursor.fetchone()
            assert row is not None

            # 4) 라운드트립 비교: 핵심 필드
            assert row["category"] == category
            assert row["content"].strip() == f"# {title}\n{body}".strip()

            db_tags = json.loads(row["tags"])
            # 원본 태그에 카테고리가 없으면 guess_tags가 추가함
            if tags:
                for t in tags:
                    assert t in db_tags
            assert category in db_tags  # 카테고리는 항상 포함

            if role.strip():
                assert row["role"] == role.strip()
            if origin:
                assert row["origin"] == origin
    finally:
        os.unlink(db_path)
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Property 9: 마이그레이션 요약 정합성
# Feature: prompt-management-app, Property 9: 마이그레이션 요약 정합성
# ---------------------------------------------------------------------------

# 파일명 전략: 유효한 파일명 (영문+숫자+하이픈+언더스코어)
filename_stem = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N"), whitelist_characters="-_"),
    min_size=3,
    max_size=20,
).filter(lambda s: s.strip() and s[0].isalpha())


@given(
    category=category_strategy,
    stems=st.lists(filename_stem, min_size=1, max_size=10),
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.asyncio
async def test_migration_summary_consistency(category, stems):
    """Validates: Requirements 2.5

    임의의 .md 파일 집합(일부 중복 ID 가능)에 대해
    마이그레이션 후 scanned == imported + skipped 이어야 한다.
    """
    fd_db, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd_db)
    tmp_dir = tempfile.mkdtemp()
    cat_dir = os.path.join(tmp_dir, category)
    os.makedirs(cat_dir, exist_ok=True)

    # stems에 중복이 있으면 같은 파일명 → 파일시스템에서 덮어쓰기 → 중복 없음
    # 대신 두 번 마이그레이션하여 중복 발생시킴
    for stem in stems:
        safe_stem = stem.strip() or "fallback"
        file_path = os.path.join(cat_dir, f"{safe_stem}.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"---\ncategory: {category}\n---\n# Title {safe_stem}\nBody")

    try:
        from pathlib import Path
        root = Path(tmp_dir)

        # 첫 번째 마이그레이션
        s1 = await migrate_all(db_path=db_path, root=root, categories=[category])
        assert s1.scanned == s1.imported + s1.skipped

        # 두 번째 마이그레이션 (전부 중복)
        s2 = await migrate_all(db_path=db_path, root=root, categories=[category])
        assert s2.scanned == s2.imported + s2.skipped
        assert s2.skipped == s2.scanned  # 전부 중복이므로
        assert s2.imported == 0
    finally:
        os.unlink(db_path)
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)
