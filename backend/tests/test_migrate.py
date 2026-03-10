"""마이그레이션 단위 테스트: frontmatter 파싱, 중복 처리, 요약 정합성.

Validates: Requirements 2.1~2.5
"""

import json
import os
import tempfile

import aiosqlite
import pytest
import pytest_asyncio

from backend.migrate import (
    extract_frontmatter,
    strip_frontmatter,
    extract_title,
    generate_id,
    parse_md_to_prompt,
    migrate_all,
    MigrationSummary,
)


# ---------------------------------------------------------------------------
# extract_frontmatter 테스트
# ---------------------------------------------------------------------------

class TestExtractFrontmatter:
    def test_valid_yaml(self):
        content = "---\ncategory: rca\ntags:\n- k8s\n- pod\nrole: SRE\n---\n# Title\nbody"
        fm = extract_frontmatter(content)
        assert fm["category"] == "rca"
        assert fm["tags"] == ["k8s", "pod"]
        assert fm["role"] == "SRE"

    def test_missing_fields(self):
        content = "---\ncategory: security\n---\n# Title\nbody"
        fm = extract_frontmatter(content)
        assert fm["category"] == "security"
        assert "tags" not in fm
        assert "role" not in fm

    def test_no_frontmatter(self):
        content = "# Just a title\nSome body text"
        fm = extract_frontmatter(content)
        assert fm == {}

    def test_malformed_yaml(self):
        content = "---\n: invalid: yaml: [[\n---\nbody"
        fm = extract_frontmatter(content)
        assert fm == {}


# ---------------------------------------------------------------------------
# strip_frontmatter 테스트
# ---------------------------------------------------------------------------

class TestStripFrontmatter:
    def test_with_frontmatter(self):
        content = "---\ncategory: rca\n---\n# Title\nbody"
        body = strip_frontmatter(content)
        assert body == "# Title\nbody"

    def test_without_frontmatter(self):
        content = "# Title\nbody"
        body = strip_frontmatter(content)
        assert body == "# Title\nbody"


# ---------------------------------------------------------------------------
# extract_title / generate_id 테스트
# ---------------------------------------------------------------------------

class TestExtractTitle:
    def test_h1_in_body(self):
        assert extract_title("# My Title\nbody", "fallback") == "My Title"

    def test_no_h1_fallback(self):
        assert extract_title("no heading here", "my-file") == "My File"


class TestGenerateId:
    def test_basic(self):
        assert generate_id("rca", "01_basic_rca") == "rca-01_basic_rca"

    def test_truncation(self):
        long_stem = "a" * 50
        result = generate_id("infrastructure", long_stem)
        assert result == f"inf-{'a' * 40}"


# ---------------------------------------------------------------------------
# 중복 처리 + 요약 정합성 (DB 필요)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def tmp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def tmp_md_dir(tmp_path):
    """테스트용 .md 파일이 있는 임시 디렉토리를 생성한다."""
    cat_dir = tmp_path / "rca"
    cat_dir.mkdir()

    (cat_dir / "test_prompt.md").write_text(
        "---\ncategory: rca\ntags:\n- test\nrole: SRE\norigin: custom\nsource: ''\n---\n# Test Prompt\nBody content",
        encoding="utf-8",
    )
    (cat_dir / "another_prompt.md").write_text(
        "---\ncategory: rca\n---\n# Another\nMore body",
        encoding="utf-8",
    )
    return tmp_path


@pytest.mark.asyncio
async def test_migrate_imports_files(tmp_db, tmp_md_dir):
    """마이그레이션이 .md 파일을 DB에 삽입한다. (Req 2.1, 2.3)"""
    summary = await migrate_all(db_path=tmp_db, root=tmp_md_dir, categories=["rca"])
    assert summary.scanned == 2
    assert summary.imported == 2
    assert summary.skipped == 0

    async with aiosqlite.connect(tmp_db) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM prompts")
        count = (await cursor.fetchone())[0]
        assert count == 2


@pytest.mark.asyncio
async def test_migrate_skips_duplicates(tmp_db, tmp_md_dir):
    """같은 ID가 이미 존재하면 스킵한다. (Req 2.4)"""
    await migrate_all(db_path=tmp_db, root=tmp_md_dir, categories=["rca"])
    summary = await migrate_all(db_path=tmp_db, root=tmp_md_dir, categories=["rca"])
    assert summary.skipped == 2
    assert summary.imported == 0


@pytest.mark.asyncio
async def test_summary_consistency(tmp_db, tmp_md_dir):
    """scanned == imported + skipped (Req 2.5)"""
    # 첫 실행: 전부 임포트
    s1 = await migrate_all(db_path=tmp_db, root=tmp_md_dir, categories=["rca"])
    assert s1.scanned == s1.imported + s1.skipped

    # 두 번째 실행: 전부 스킵
    s2 = await migrate_all(db_path=tmp_db, root=tmp_md_dir, categories=["rca"])
    assert s2.scanned == s2.imported + s2.skipped


@pytest.mark.asyncio
async def test_parsed_fields_stored_correctly(tmp_db, tmp_md_dir):
    """파싱된 필드가 DB에 올바르게 저장된다. (Req 2.2, 2.3)"""
    await migrate_all(db_path=tmp_db, root=tmp_md_dir, categories=["rca"])

    async with aiosqlite.connect(tmp_db) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM prompts WHERE id = ?", ("rca-test_prompt",))
        row = await cursor.fetchone()
        assert row is not None
        assert row["title"] == "Test Prompt"
        assert row["category"] == "rca"
        assert row["role"] == "SRE"
        assert "test" in json.loads(row["tags"])
        assert row["content"] == "# Test Prompt\nBody content"
