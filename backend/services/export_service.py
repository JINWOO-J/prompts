"""익스포트/동기화 비즈니스 로직."""

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import yaml
import aiosqlite

from backend.models import ExportSummary, PromptCreate, PromptResponse
from backend.services.prompt_service import list_prompts

CATEGORIES = [
    "rca", "incident-response", "application", "infrastructure",
    "security", "data-ai", "shared", "techniques", "coding",
]

# 프로젝트 루트 (md 파일 기준 경로)
_PROJECT_ROOT = Path(__file__).parent.parent.parent


def sync_prompt_to_md(prompt: PromptResponse) -> Path:
    """단일 프롬프트를 md 파일로 즉시 동기화한다. 반환: 작성된 파일 경로."""
    rel_path = _prompt_file_path(prompt)
    full_path = _PROJECT_ROOT / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(format_prompt_as_md(prompt), encoding="utf-8")
    return full_path


def delete_prompt_md(prompt: PromptResponse) -> Path | None:
    """프롬프트에 해당하는 md 파일을 삭제한다. 없으면 None."""
    rel_path = _prompt_file_path(prompt)
    full_path = _PROJECT_ROOT / rel_path
    if full_path.exists():
        full_path.unlink()
        return full_path
    return None


def format_prompt_as_md(prompt: PromptResponse) -> str:
    """PromptResponse를 YAML frontmatter + 마크다운 본문 형식으로 변환한다."""
    frontmatter = {
        "category": prompt.category,
        "origin": prompt.origin,
        "source": prompt.source,
        "tags": prompt.tags,
        "role": prompt.role,
    }
    fm_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False).rstrip("\n")
    return f"---\n{fm_str}\n---\n{prompt.content}"


def parse_md_file(file_path: Path) -> PromptCreate:
    """YAML frontmatter가 있는 .md 파일을 파싱하여 PromptCreate로 변환한다."""
    text = file_path.read_text(encoding="utf-8")

    # frontmatter 추출
    fm: dict = {}
    body = text
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            try:
                fm = yaml.safe_load(text[3:end]) or {}
            except Exception:
                fm = {}
            body = text[end + 3:].lstrip("\n")

    return PromptCreate(
        title=file_path.stem.replace("-", " ").replace("_", " ").title(),
        category=fm.get("category", ""),
        content=body,
        tags=fm.get("tags", []) if isinstance(fm.get("tags"), list) else [],
        role=fm.get("role", ""),
    )


def _prompt_file_path(prompt: PromptResponse) -> Path:
    """프롬프트의 익스포트 파일 경로를 결정한다."""
    if prompt.file_path:
        return Path(prompt.file_path)
    # file_path가 없으면 category/id.md 사용
    return Path(prompt.category) / f"{prompt.id}.md"


async def export_all_to_md(db: aiosqlite.Connection, output_dir: str) -> ExportSummary:
    """DB의 모든 프롬프트를 .md 파일로 익스포트한다."""
    out = Path(output_dir)
    count = 0

    # 전체 프롬프트 조회 (큰 page_size로 한 번에)
    result = await list_prompts(db, page_size=10000)
    # 각 프롬프트의 전체 데이터가 필요하므로 개별 조회
    from backend.services.prompt_service import get_prompt

    for item in result.prompts:
        prompt = await get_prompt(db, item.id)
        if not prompt:
            continue

        rel_path = _prompt_file_path(prompt)
        full_path = out / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(format_prompt_as_md(prompt), encoding="utf-8")
        count += 1

    return ExportSummary(total_exported=count, output_directory=str(out))


async def sync_meta_files(db: aiosqlite.Connection, project_root: str) -> ExportSummary:
    """prompts.meta.yaml과 web/data.json을 DB 상태로 재생성한다."""
    root = Path(project_root)
    from backend.services.prompt_service import get_prompt

    result = await list_prompts(db, page_size=10000)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # 카테고리별 통계
    stats: Counter = Counter()
    prompts_meta: list[dict] = []
    prompts_data: list[dict] = []

    for item in result.prompts:
        stats[item.category] += 1
        prompt = await get_prompt(db, item.id)
        if not prompt:
            continue

        rel_path = str(_prompt_file_path(prompt))
        meta_entry = {
            "id": prompt.id,
            "file": rel_path,
            "title": prompt.title,
            "category": prompt.category,
            "origin": prompt.origin,
            "tags": prompt.tags,
        }
        prompts_meta.append(meta_entry)
        prompts_data.append({**meta_entry, "content": prompt.content})

    meta_doc = {
        "_meta": {
            "version": "4.0",
            "generated": now,
            "total": result.total,
            "stats": {cat: stats.get(cat, 0) for cat in CATEGORIES},
            "categories": CATEGORIES,
        },
        "prompts": prompts_meta,
    }

    data_doc = {
        "_meta": meta_doc["_meta"],
        "prompts": prompts_data,
    }

    # 파일 쓰기
    meta_path = root / "prompts.meta.yaml"
    meta_path.write_text(yaml.dump(meta_doc, allow_unicode=True, default_flow_style=False), encoding="utf-8")

    data_path = root / "web" / "data.json"
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(data_doc, ensure_ascii=False, indent=2), encoding="utf-8")

    return ExportSummary(total_exported=result.total, output_directory=str(root))
