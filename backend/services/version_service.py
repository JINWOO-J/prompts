"""버전 관리 비즈니스 로직."""

import json
from datetime import datetime, timezone

import aiosqlite

from backend.models import PromptResponse, VersionResponse


def _row_to_version(row: aiosqlite.Row) -> VersionResponse:
    return VersionResponse(
        id=row["id"],
        prompt_id=row["prompt_id"],
        title=row["title"],
        content=row["content"],
        tags=json.loads(row["tags"]),
        version_number=row["version_number"],
        created_at=row["created_at"],
        change_summary=row["change_summary"] or "",
    )


async def _next_version_number(db: aiosqlite.Connection, prompt_id: str) -> int:
    """해당 prompt_id의 다음 version_number를 반환한다."""
    cursor = await db.execute(
        "SELECT MAX(version_number) FROM versions WHERE prompt_id = ?",
        (prompt_id,),
    )
    row = await cursor.fetchone()
    return (row[0] or 0) + 1


async def create_version(
    db: aiosqlite.Connection,
    prompt_id: str,
    current_prompt: PromptResponse,
    change_summary: str = "",
) -> VersionResponse:
    """현재 프롬프트 상태를 버전으로 저장한다."""
    now = datetime.now(timezone.utc).isoformat()
    version_number = await _next_version_number(db, prompt_id)

    cursor = await db.execute(
        """INSERT INTO versions
           (prompt_id, title, content, tags, version_number, created_at, change_summary)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            prompt_id,
            current_prompt.title,
            current_prompt.content,
            json.dumps(current_prompt.tags, ensure_ascii=False),
            version_number,
            now,
            change_summary,
        ),
    )
    await db.commit()

    # 방금 삽입한 레코드 조회
    fetch = await db.execute("SELECT * FROM versions WHERE id = ?", (cursor.lastrowid,))
    row = await fetch.fetchone()
    return _row_to_version(row)


async def list_versions(
    db: aiosqlite.Connection, prompt_id: str
) -> list[VersionResponse]:
    """해당 프롬프트의 버전 목록을 version_number 내림차순으로 반환한다."""
    rows = await db.execute_fetchall(
        "SELECT * FROM versions WHERE prompt_id = ? ORDER BY version_number DESC",
        (prompt_id,),
    )
    return [_row_to_version(r) for r in rows]


async def get_version(
    db: aiosqlite.Connection, prompt_id: str, version_number: int
) -> VersionResponse | None:
    """특정 버전을 반환한다. 없으면 None."""
    cursor = await db.execute(
        "SELECT * FROM versions WHERE prompt_id = ? AND version_number = ?",
        (prompt_id, version_number),
    )
    row = await cursor.fetchone()
    return _row_to_version(row) if row else None


async def restore_version(
    db: aiosqlite.Connection, prompt_id: str, version_number: int
) -> PromptResponse | None:
    """지정된 버전으로 프롬프트를 복원한다. 복원 전 현재 상태를 새 버전으로 저장한다."""
    from backend.services.prompt_service import get_prompt

    # 복원할 버전 조회
    version = await get_version(db, prompt_id, version_number)
    if not version:
        return None

    # 현재 프롬프트 조회
    current = await get_prompt(db, prompt_id)
    if not current:
        return None

    # 현재 상태를 새 버전으로 저장 (복원 행위 기록)
    await create_version(
        db, prompt_id, current,
        change_summary=f"Before restore to v{version_number}",
    )

    # 프롬프트를 버전 내용으로 업데이트
    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        """UPDATE prompts
           SET title = ?, content = ?, tags = ?, updated_at = ?
           WHERE id = ?""",
        (
            version.title,
            version.content,
            json.dumps(version.tags, ensure_ascii=False),
            now,
            prompt_id,
        ),
    )
    await db.commit()

    return await get_prompt(db, prompt_id)
