"""AI 개선 제안 라우터."""

from fastapi import APIRouter, Depends, HTTPException, Query

import aiosqlite

from backend.database import get_db
from backend.models import AIStatusResponse, SuggestionResponse
from backend.services.ai_service import check_ai_available, suggest_improvement
from backend.services.prompt_service import get_prompt
from backend.services.suggestion_service import (
    ConflictError,
    accept_suggestion,
    create_suggestion,
    get_suggestion,
    list_suggestions,
    reject_suggestion,
)

router = APIRouter(tags=["suggestions"])


@router.get("/api/ai/status", response_model=AIStatusResponse)
async def ai_status():
    """LLM API 사용 가능 여부를 반환한다."""
    return AIStatusResponse(available=check_ai_available())


@router.post(
    "/api/prompts/{prompt_id}/suggest",
    response_model=SuggestionResponse,
    status_code=201,
)
async def suggest_endpoint(
    prompt_id: str,
    db: aiosqlite.Connection = Depends(get_db),
):
    """AI에게 프롬프트 개선을 요청하고 제안을 저장한다."""
    prompt = await get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail=f"Prompt not found: {prompt_id}")

    if not check_ai_available():
        raise HTTPException(status_code=503, detail="AI service is not configured (LLM_API_KEY missing)")

    try:
        ai_result = await suggest_improvement(prompt.content, prompt.category)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {e}")
    except Exception as e:
        # httpx.TimeoutException, httpx.HTTPStatusError 등
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"AI service unavailable: {type(e).__name__}: {e}")

    ai_result["original_content"] = prompt.content
    suggestion = await create_suggestion(db, prompt_id, ai_result)
    return suggestion


@router.get(
    "/api/prompts/{prompt_id}/suggestions",
    response_model=list[SuggestionResponse],
)
async def list_suggestions_endpoint(
    prompt_id: str,
    status: str | None = Query(None),
    db: aiosqlite.Connection = Depends(get_db),
):
    """프롬프트별 제안 목록을 반환한다."""
    prompt = await get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail=f"Prompt not found: {prompt_id}")
    return await list_suggestions(db, prompt_id, status=status)


@router.post(
    "/api/prompts/{prompt_id}/suggestions/{suggestion_id}/accept",
    response_model=SuggestionResponse,
)
async def accept_suggestion_endpoint(
    prompt_id: str,
    suggestion_id: int,
    db: aiosqlite.Connection = Depends(get_db),
):
    """제안을 수락하고 프롬프트를 업데이트한다."""
    suggestion = await get_suggestion(db, suggestion_id)
    if not suggestion or suggestion.prompt_id != prompt_id:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    try:
        return await accept_suggestion(db, suggestion_id)
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/api/prompts/{prompt_id}/suggestions/{suggestion_id}/reject",
    response_model=SuggestionResponse,
)
async def reject_suggestion_endpoint(
    prompt_id: str,
    suggestion_id: int,
    db: aiosqlite.Connection = Depends(get_db),
):
    """제안을 거절한다."""
    suggestion = await get_suggestion(db, suggestion_id)
    if not suggestion or suggestion.prompt_id != prompt_id:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    try:
        return await reject_suggestion(db, suggestion_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
