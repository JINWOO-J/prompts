"""개선 제안 CRUD 비즈니스 로직."""

import json
from datetime import datetime, timezone

import aiosqlite

from backend.models import SuggestionResponse


def _row_to_suggestion(row: aiosqlite.Row) -> SuggestionResponse:
    return SuggestionResponse(
        id=row["id"],
        prompt_id=row["prompt_id"],
        original_content=row["original_content"],
        suggested_content=row["suggested_content"],
        reason=row["reason"],
        status=row["status"],
        created_at=row["created_at"],
        resolved_at=row["resolved_at"],
    )


async def create_suggestion(
    db: aiosqlite.Connection,
    prompt_id: str,
    ai_result: dict,
    requested_by: str | None = None,
) -> SuggestionResponse:
    """AI 개선 제안을 저장한다. 동일 프롬프트에 대해 pending 상태가 있으면 기존 것을 반환한다."""
    # 기존 pending 제안 확인
    cursor = await db.execute(
        "SELECT * FROM suggestions WHERE prompt_id = ? AND status = 'pending' LIMIT 1",
        (prompt_id,),
    )
    existing = await cursor.fetchone()
    if existing:
        return _row_to_suggestion(existing)

    now = datetime.now(timezone.utc).isoformat()
    cursor = await db.execute(
        """INSERT INTO suggestions
           (prompt_id, original_content, suggested_content, reason, status, requested_by, created_at)
           VALUES (?, ?, ?, ?, 'pending', ?, ?)""",
        (
            prompt_id,
            ai_result["original_content"],
            ai_result["improved_content"],
            ai_result["reason"],
            requested_by,
            now,
        ),
    )
    await db.commit()

    fetch = await db.execute("SELECT * FROM suggestions WHERE id = ?", (cursor.lastrowid,))
    row = await fetch.fetchone()
    return _row_to_suggestion(row)


async def get_suggestion(
    db: aiosqlite.Connection, suggestion_id: int
) -> SuggestionResponse | None:
    """단건 제안을 반환한다. 없으면 None."""
    cursor = await db.execute("SELECT * FROM suggestions WHERE id = ?", (suggestion_id,))
    row = await cursor.fetchone()
    return _row_to_suggestion(row) if row else None


async def list_suggestions(
    db: aiosqlite.Connection,
    prompt_id: str,
    status: str | None = None,
) -> list[SuggestionResponse]:
    """프롬프트별 제안 목록을 반환한다. status 필터 선택 가능."""
    if status:
        rows = await db.execute_fetchall(
            "SELECT * FROM suggestions WHERE prompt_id = ? AND status = ? ORDER BY created_at DESC",
            (prompt_id, status),
        )
    else:
        rows = await db.execute_fetchall(
            "SELECT * FROM suggestions WHERE prompt_id = ? ORDER BY created_at DESC",
            (prompt_id,),
        )
    return [_row_to_suggestion(r) for r in rows]


async def accept_suggestion(
    db: aiosqlite.Connection, suggestion_id: int
) -> SuggestionResponse:
    """제안을 수락한다. 프롬프트를 업데이트하고 버전을 생성한다.

    Raises:
        ValueError: 제안이 없거나 pending 상태가 아닌 경우
        ConflictError: 원본 내용이 현재 프롬프트와 다른 경우
    """
    from backend.services.prompt_service import get_prompt
    from backend.services.version_service import create_version

    suggestion = await get_suggestion(db, suggestion_id)
    if not suggestion:
        raise ValueError("Suggestion not found")
    if suggestion.status != "pending":
        raise ValueError(f"Suggestion is already {suggestion.status}")

    # 현재 프롬프트 조회
    prompt = await get_prompt(db, suggestion.prompt_id)
    if not prompt:
        raise ValueError("Associated prompt not found")

    # 충돌 검사: 제안 생성 시점의 원본과 현재 내용이 다르면 충돌
    if prompt.content != suggestion.original_content:
        raise ConflictError(
            "Prompt content has changed since suggestion was created. "
            "Please reject this suggestion and request a new one."
        )

    # 현재 상태를 버전으로 저장
    await create_version(
        db, suggestion.prompt_id, prompt,
        change_summary="Before AI suggestion accepted",
    )

    # 프롬프트 업데이트
    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        "UPDATE prompts SET content = ?, updated_at = ? WHERE id = ?",
        (suggestion.suggested_content, now, suggestion.prompt_id),
    )

    # 제안 상태 업데이트
    await db.execute(
        "UPDATE suggestions SET status = 'accepted', resolved_at = ? WHERE id = ?",
        (now, suggestion_id),
    )
    await db.commit()

    # 파일 동기화 (export_service가 있는 경우)
    try:
        from backend.services.export_service import sync_meta_files
        from pathlib import Path
        project_root = str(Path(__file__).parent.parent.parent)
        await sync_meta_files(db, project_root)
    except ImportError:
        pass

    return await get_suggestion(db, suggestion_id)  # type: ignore[return-value]


async def reject_suggestion(
    db: aiosqlite.Connection, suggestion_id: int
) -> SuggestionResponse:
    """제안을 거절한다.

    Raises:
        ValueError: 제안이 없거나 pending 상태가 아닌 경우
    """
    suggestion = await get_suggestion(db, suggestion_id)
    if not suggestion:
        raise ValueError("Suggestion not found")
    if suggestion.status != "pending":
        raise ValueError(f"Suggestion is already {suggestion.status}")

    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        "UPDATE suggestions SET status = 'rejected', resolved_at = ? WHERE id = ?",
        (now, suggestion_id),
    )
    await db.commit()

    return await get_suggestion(db, suggestion_id)  # type: ignore[return-value]


class ConflictError(Exception):
    """프롬프트 내용이 제안 생성 이후 변경된 경우 발생한다."""
    pass
