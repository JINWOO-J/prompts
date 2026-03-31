"""프롬프트 CRUD 비즈니스 로직."""

import json
import re
from datetime import datetime, timezone

import aiosqlite

from backend.models import (
    PromptCreate,
    PromptListItem,
    PromptListResponse,
    PromptResponse,
    PromptUpdate,
)


def _slugify(text: str) -> str:
    """제목을 URL-safe slug로 변환한다."""
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9가-힣\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")[:40]


def _generate_id(category: str, title: str) -> str:
    """프롬프트 ID 생성: {category[:3]}-{slugified_title}"""
    return f"{category[:3]}-{_slugify(title)}"


def _row_to_response(row: aiosqlite.Row) -> PromptResponse:
    return PromptResponse(
        id=row["id"],
        title=row["title"],
        category=row["category"],
        content=row["content"],
        tags=json.loads(row["tags"]),
        role=row["role"],
        origin=row["origin"],
        source=row["source"],
        file_path=row["file_path"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _row_to_list_item(row: aiosqlite.Row) -> PromptListItem:
    return PromptListItem(
        id=row["id"],
        title=row["title"],
        category=row["category"],
        tags=json.loads(row["tags"]),
        role=row["role"],
        origin=row["origin"],
        updated_at=row["updated_at"],
    )


async def list_prompts(
    db: aiosqlite.Connection,
    q: str | None = None,
    category: str | None = None,
    tag: str | None = None,
    page: int = 1,
    page_size: int = 50,
) -> PromptListResponse:
    """페이지네이션 + 필터링된 프롬프트 목록을 반환한다."""
    conditions: list[str] = []
    params: list[str] = []

    if q:
        conditions.append("(title LIKE ? OR content LIKE ?)")
        params.extend([f"%{q}%", f"%{q}%"])
    if category:
        conditions.append("category = ?")
        params.append(category)
    if tag:
        conditions.append("tags LIKE ?")
        params.append(f'%"{tag}"%')

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    # 전체 개수
    count_row = await db.execute_fetchall(
        f"SELECT COUNT(*) FROM prompts {where}", params
    )
    total = count_row[0][0]

    # 페이지네이션
    offset = (page - 1) * page_size
    rows = await db.execute_fetchall(
        f"SELECT * FROM prompts {where} ORDER BY updated_at DESC LIMIT ? OFFSET ?",
        [*params, page_size, offset],
    )

    return PromptListResponse(
        total=total,
        page=page,
        page_size=page_size,
        prompts=[_row_to_list_item(r) for r in rows],
    )


async def get_prompt(
    db: aiosqlite.Connection, prompt_id: str
) -> PromptResponse | None:
    """단건 프롬프트를 반환한다. 없으면 None."""
    cursor = await db.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,))
    row = await cursor.fetchone()
    return _row_to_response(row) if row else None


async def create_prompt(
    db: aiosqlite.Connection, data: PromptCreate
) -> PromptResponse:
    """프롬프트를 생성하고 반환한다."""
    now = datetime.now(timezone.utc).isoformat()
    prompt_id = data.id or _generate_id(data.category, data.title)

    await db.execute(
        """INSERT INTO prompts
           (id, title, category, content, tags, role, origin, source, file_path, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, '', '', '', ?, ?)""",
        (
            prompt_id, data.title, data.category, data.content,
            json.dumps(data.tags, ensure_ascii=False), data.role,
            now, now,
        ),
    )
    await db.commit()

    result = await get_prompt(db, prompt_id)  # type: ignore[return-value]
    # md 파일 동기화
    from backend.services.export_service import sync_prompt_to_md
    sync_prompt_to_md(result)
    return result


async def update_prompt(
    db: aiosqlite.Connection, prompt_id: str, data: PromptUpdate
) -> PromptResponse | None:
    """제공된 필드만 업데이트한다. 업데이트 전 현재 상태를 버전으로 저장한다. 없으면 None."""
    from backend.services.version_service import create_version

    existing = await get_prompt(db, prompt_id)
    if not existing:
        return None

    # 업데이트 전 현재 상태를 버전으로 저장
    await create_version(db, prompt_id, existing, change_summary=data.change_summary)

    now = datetime.now(timezone.utc).isoformat()
    fields: dict = {}
    if data.title is not None:
        fields["title"] = data.title
    if data.content is not None:
        fields["content"] = data.content
    if data.category is not None:
        fields["category"] = data.category
    if data.tags is not None:
        fields["tags"] = json.dumps(data.tags, ensure_ascii=False)
    if data.role is not None:
        fields["role"] = data.role
    fields["updated_at"] = now

    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [prompt_id]

    await db.execute(
        f"UPDATE prompts SET {set_clause} WHERE id = ?", values
    )
    await db.commit()

    result = await get_prompt(db, prompt_id)
    # md 파일 동기화
    from backend.services.export_service import sync_prompt_to_md
    sync_prompt_to_md(result)
    return result


async def delete_prompt(db: aiosqlite.Connection, prompt_id: str) -> bool:
    """프롬프트를 삭제한다. CASCADE로 버전도 삭제됨. 없으면 False."""
    # 삭제 전 md 파일 제거를 위해 조회
    existing = await get_prompt(db, prompt_id)
    cursor = await db.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
    await db.commit()
    if cursor.rowcount > 0 and existing:
        from backend.services.export_service import delete_prompt_md
        delete_prompt_md(existing)
        return True
    return cursor.rowcount > 0
