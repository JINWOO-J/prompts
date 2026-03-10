"""프롬프트 CRUD 라우터."""

from fastapi import APIRouter, Depends, HTTPException, Query

import aiosqlite

from backend.database import get_db
from backend.models import (
    PromptCreate,
    PromptListResponse,
    PromptResponse,
    PromptUpdate,
)
from backend.services.prompt_service import (
    create_prompt,
    delete_prompt,
    get_prompt,
    list_prompts,
    update_prompt,
)

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


@router.get("", response_model=PromptListResponse)
async def list_prompts_endpoint(
    q: str | None = None,
    category: str | None = None,
    tag: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: aiosqlite.Connection = Depends(get_db),
):
    return await list_prompts(db, q=q, category=category, tag=tag, page=page, page_size=page_size)


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt_endpoint(
    prompt_id: str,
    db: aiosqlite.Connection = Depends(get_db),
):
    result = await get_prompt(db, prompt_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Prompt not found: {prompt_id}")
    return result


@router.post("", response_model=PromptResponse, status_code=201)
async def create_prompt_endpoint(
    data: PromptCreate,
    db: aiosqlite.Connection = Depends(get_db),
):
    return await create_prompt(db, data)


@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt_endpoint(
    prompt_id: str,
    data: PromptUpdate,
    db: aiosqlite.Connection = Depends(get_db),
):
    result = await update_prompt(db, prompt_id, data)
    if not result:
        raise HTTPException(status_code=404, detail=f"Prompt not found: {prompt_id}")
    return result


@router.delete("/{prompt_id}", status_code=204)
async def delete_prompt_endpoint(
    prompt_id: str,
    db: aiosqlite.Connection = Depends(get_db),
):
    deleted = await delete_prompt(db, prompt_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Prompt not found: {prompt_id}")
