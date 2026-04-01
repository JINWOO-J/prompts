"""마크다운 → DB 마이그레이션."""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite

from backend.database import DB_PATH, init_db

logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent
CATEGORIES = [
    "rca", "incident-response", "application", "infrastructure",
    "security", "data-ai", "shared", "techniques", "coding",
]


# ---------------------------------------------------------------------------
# Frontmatter / 본문 파싱
# ---------------------------------------------------------------------------

def extract_frontmatter(content: str) -> dict:
    import yaml
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
    if not content.startswith("---"):
        return content
    end = content.find("---", 3)
    if end == -1:
        return content
    return content[end + 3:].lstrip("\n")


# ---------------------------------------------------------------------------
# 제목 / ID / 태그 / origin
# ---------------------------------------------------------------------------

def extract_title(body: str, stem: str) -> str:
    m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if m:
        return m.group(1).strip()[:80]
    return _title_from_filename(stem)[:80]


def _title_from_filename(stem: str) -> str:
    if stem.startswith("agent-"):
        role = stem[6:].replace("-", " ").title()
        return f"Agent: {role}"
    m = re.match(r"aws-\d+-([A-Za-z]+)-(.+)", stem)
    if m:
        return f"{m.group(1)}: {m.group(2).replace('-', ' ')}"
    m = re.match(r"k8s-\d+-([A-Za-z-]+)-(.+)", stem)
    if m:
        return f"K8s {m.group(1).replace('-', ' ')}: {m.group(2).replace('-', ' ')}"
    if stem.startswith("sentry-"):
        return f"Sentry: {stem[7:].replace('-', ' ')}"
    return stem.replace("-", " ").replace("_", " ").title()


def generate_id(category: str, stem: str) -> str:
    return f"{category[:3]}-{stem[:40]}"


def guess_origin(fname: str, fm: dict) -> str:
    if fm.get("origin"):
        return fm["origin"]
    if fname.startswith("aws-") or fname.startswith("k8s-"):
        return "scoutflo"
    if fname.startswith("agent-"):
        return "voltagent"
    return "custom"


def guess_tags(fname: str, category: str, fm: dict) -> list:
    if fm.get("tags") and isinstance(fm["tags"], list):
        tags = list(fm["tags"])
        if category not in tags:
            tags.insert(0, category)
        return list(dict.fromkeys(tags))
    return [category]


# ---------------------------------------------------------------------------
# 언어 쌍 처리
# ---------------------------------------------------------------------------

def _base_stem(filename: str) -> tuple[str, str]:
    """파일명에서 base stem과 언어 코드를 추출."""
    stem = Path(filename).stem
    if stem.endswith(".ko"):
        return stem[:-3], "ko"
    if stem.endswith(".en"):
        return stem[:-3], "en"
    return stem, ""


# ---------------------------------------------------------------------------
# 마이그레이션
# ---------------------------------------------------------------------------

@dataclass
class MigrationSummary:
    scanned: int = 0
    imported: int = 0
    skipped: int = 0


def scan_md_pairs(root: Path, categories: list[str] | None = None) -> list[tuple[str, dict[str, Path], str]]:
    """언어별 파일을 쌍으로 묶어 반환."""
    cats = categories or CATEGORIES
    results = []
    for cat in cats:
        cat_dir = root / cat
        if not cat_dir.exists():
            continue
        paired: dict[str, dict[str, Path]] = {}
        for f in sorted(cat_dir.glob("*.md")):
            base, lang = _base_stem(f.name)
            if base not in paired:
                paired[base] = {}
            paired[base][lang or "ko"] = f
        for base, lang_files in sorted(paired.items()):
            results.append((base, lang_files, cat))
    return results


def parse_md_pair(base_stem: str, lang_files: dict[str, Path], category: str) -> dict:
    """언어 쌍 파일을 파싱하여 DB 삽입용 dict를 반환한다."""
    primary = lang_files.get("ko") or lang_files.get("en")
    if not primary:
        raise ValueError(f"No primary file for {base_stem}")

    content = primary.read_text(encoding="utf-8")
    fm = extract_frontmatter(content)
    body = strip_frontmatter(content)

    now = datetime.now(timezone.utc).isoformat()

    content_en = ""
    en_file = lang_files.get("en")
    if en_file and en_file != primary:
        en_content = en_file.read_text(encoding="utf-8")
        content_en = strip_frontmatter(en_content)

    return {
        "id": generate_id(category, base_stem),
        "title": extract_title(body, base_stem),
        "category": fm.get("category", category),
        "content": body,
        "content_en": content_en,
        "tags": json.dumps(guess_tags(primary.name, category, fm), ensure_ascii=False),
        "type": fm.get("type", "prompt"),
        "role": fm.get("role", ""),
        "origin": guess_origin(primary.name, fm),
        "source": fm.get("source", ""),
        "file_path": f"{category}/{primary.name}",
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
    pairs = scan_md_pairs(root, categories)
    summary = MigrationSummary(scanned=len(pairs))

    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        for base_stem, lang_files, category in pairs:
            prompt = parse_md_pair(base_stem, lang_files, category)
            cursor = await db.execute(
                "SELECT 1 FROM prompts WHERE id = ?", (prompt["id"],)
            )
            if await cursor.fetchone():
                logger.warning("중복 스킵: %s", prompt["id"])
                summary.skipped += 1
                continue

            await db.execute(
                """INSERT INTO prompts
                   (id, title, category, content, content_en, tags, type, role, origin, source, file_path, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    prompt["id"], prompt["title"], prompt["category"],
                    prompt["content"], prompt["content_en"], prompt["tags"],
                    prompt["type"], prompt["role"],
                    prompt["origin"], prompt["source"], prompt["file_path"],
                    prompt["created_at"], prompt["updated_at"],
                ),
            )
            summary.imported += 1

        await db.commit()

    return summary


# ---------------------------------------------------------------------------
# export_service에서 사용하는 하위 호환 함수
# ---------------------------------------------------------------------------

def scan_md_files(root: Path, categories: list[str] | None = None) -> list[tuple[Path, str]]:
    """하위 호환용 — 모든 .md 파일을 flat 리스트로 반환."""
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
    """하위 호환용 — 단일 파일 파싱."""
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
        "content_en": "",
        "tags": json.dumps(guess_tags(file_path.name, category, fm), ensure_ascii=False),
        "type": fm.get("type", "prompt"),
        "role": fm.get("role", ""),
        "origin": guess_origin(file_path.name, fm),
        "source": fm.get("source", ""),
        "file_path": f"{category}/{file_path.name}",
        "created_at": now,
        "updated_at": now,
    }
