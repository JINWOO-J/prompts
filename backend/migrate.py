"""기존 .md 파일을 SQLite DB로 마이그레이션하는 스크립트.

실행: python -m backend.migrate
"""

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import yaml
import aiosqlite

from backend.database import init_db, DB_PATH

logger = logging.getLogger(__name__)

CATEGORIES = [
    "rca", "incident-response", "application", "infrastructure",
    "security", "data-ai", "shared", "techniques", "coding",
]

ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# 파싱 유틸리티
# ---------------------------------------------------------------------------

def extract_frontmatter(content: str) -> dict:
    """YAML frontmatter를 파싱하여 dict로 반환한다. 없으면 빈 dict."""
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(content[3:end]) or {}
    except Exception:
        return {}


def strip_frontmatter(content: str) -> str:
    """YAML frontmatter를 제거하고 마크다운 본문만 반환한다."""
    if not content.startswith("---"):
        return content
    end = content.find("---", 3)
    if end == -1:
        return content
    return content[end + 3:].lstrip("\n")


def _title_from_filename(stem: str) -> str:
    """파일명에서 의미 있는 제목을 생성한다. rebuild-index.py 로직 재사용."""
    if stem.startswith("agent-"):
        role = stem[6:].replace("-", " ").title()
        return f"Agent: {role}"

    m = re.match(r"aws-\d+-([A-Za-z]+)-(.+)", stem)
    if m:
        return f"{m.group(1)}: {m.group(2).replace('-', ' ')}"

    m = re.match(r"k8s-\d+-([A-Za-z-]+)-(.+)", stem)
    if m:
        section = m.group(1).replace("-", " ")
        rest = m.group(2).replace("-", " ")
        return f"K8s {section}: {rest}"

    if stem.startswith("sentry-"):
        return f"Sentry: {stem[7:].replace('-', ' ')}"

    return stem.replace("-", " ").replace("_", " ").title()


def extract_title(body: str, stem: str) -> str:
    """본문에서 첫 H1을 추출한다. 없으면 파일명 기반 제목."""
    m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if m:
        return m.group(1).strip()[:80]
    return _title_from_filename(stem)


def guess_origin(fname: str, fm: dict) -> str:
    """origin 필드를 결정한다. frontmatter 우선, 없으면 파일명 기반 추론."""
    if fm.get("origin"):
        return fm["origin"]
    if fname.startswith("aws-") or fname.startswith("k8s-") or fname.startswith("sentry-"):
        return "scoutflo"
    if fname.startswith("agent-"):
        return "voltagent"
    return "custom"


def guess_tags(fname: str, category: str, fm: dict) -> list[str]:
    """태그를 결정한다. frontmatter 우선, 없으면 카테고리만."""
    if fm.get("tags") and isinstance(fm["tags"], list):
        tags = list(fm["tags"])
        if category not in tags:
            tags.insert(0, category)
        return list(dict.fromkeys(tags))
    return [category]


def generate_id(category: str, stem: str) -> str:
    """프롬프트 ID를 생성한다: {cat[:3]}-{stem[:40]}"""
    return f"{category[:3]}-{stem[:40]}"


# ---------------------------------------------------------------------------
# 마이그레이션 핵심 로직
# ---------------------------------------------------------------------------

@dataclass
class MigrationSummary:
    scanned: int = 0
    imported: int = 0
    skipped: int = 0


def scan_md_files(root: Path, categories: list[str] | None = None) -> list[tuple[Path, str]]:
    """카테고리 디렉토리에서 .md 파일을 스캔한다. (파일경로, 카테고리) 튜플 리스트 반환."""
    cats = categories or CATEGORIES
    results: list[tuple[Path, str]] = []
    for cat in cats:
        cat_dir = root / cat
        if not cat_dir.exists():
            continue
        for f in sorted(cat_dir.glob("*.md")):
            results.append((f, cat))
    return results


def parse_md_to_prompt(file_path: Path, category: str) -> dict:
    """단일 .md 파일을 파싱하여 DB 삽입용 dict를 반환한다."""
    content = file_path.read_text(encoding="utf-8")
    fm = extract_frontmatter(content)
    body = strip_frontmatter(content)

    stem = file_path.stem
    now = datetime.now(timezone.utc).isoformat()

    return {
        "id": generate_id(category, stem),
        "title": extract_title(body, stem),
        "category": fm.get("category", category),
        "content": body,
        "tags": json.dumps(guess_tags(file_path.name, category, fm), ensure_ascii=False),
        "type": fm.get("type", "prompt"),
        "role": fm.get("role", ""),
        "origin": guess_origin(file_path.name, fm),
        "source": fm.get("source", ""),
        "file_path": f"{category}/{file_path.name}",
        "created_at": now,
        "updated_at": now,
    }


async def migrate_all(
    db_path: str = DB_PATH,
    root: Path = ROOT,
    categories: list[str] | None = None,
) -> MigrationSummary:
    """모든 .md 파일을 스캔하여 DB에 삽입한다."""
    await init_db(db_path=db_path)
    files = scan_md_files(root, categories)
    summary = MigrationSummary(scanned=len(files))

    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        for file_path, category in files:
            prompt = parse_md_to_prompt(file_path, category)
            # 중복 체크
            cursor = await db.execute(
                "SELECT 1 FROM prompts WHERE id = ?", (prompt["id"],)
            )
            if await cursor.fetchone():
                logger.warning("중복 스킵: %s (%s)", prompt["id"], file_path)
                summary.skipped += 1
                continue

            await db.execute(
                """INSERT INTO prompts
                   (id, title, category, content, tags, type, role, origin, source, file_path, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    prompt["id"], prompt["title"], prompt["category"],
                    prompt["content"], prompt["tags"], prompt["type"], prompt["role"],
                    prompt["origin"], prompt["source"], prompt["file_path"],
                    prompt["created_at"], prompt["updated_at"],
                ),
            )
            summary.imported += 1

        await db.commit()

    return summary


# ---------------------------------------------------------------------------
# CLI 엔트리포인트
# ---------------------------------------------------------------------------

async def _main():
    print("🔄 마이그레이션 시작...")
    summary = await migrate_all()
    print(f"✅ 완료 — 스캔: {summary.scanned}, 임포트: {summary.imported}, 스킵: {summary.skipped}")


if __name__ == "__main__":
    asyncio.run(_main())
