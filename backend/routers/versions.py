"""버전 히스토리 라우터."""

from fastapi import APIRouter, Depends, HTTPException

import aiosqlite

from backend.database import get_db
from backend.models import PromptResponse, VersionResponse
from backend.services.prompt_service import get_prompt
from backend.services.version_service import (
    get_version,
    list_versions,
    restore_version,
)

router = APIRouter(prefix="/api/prompts/{prompt_id}/versions", tags=["versions"])


@router.get("", response_model=list[VersionResponse])
async def list_versions_endpoint(
    prompt_id: str,
    db: aiosqlite.Connection = Depends(get_db),
):
    prompt = await get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail=f"Prompt not found: {prompt_id}")
    return await list_versions(db, prompt_id)


@router.get("/{version_number}", response_model=VersionResponse)
async def get_version_endpoint(
    prompt_id: str,
    version_number: int,
    db: aiosqlite.Connection = Depends(get_db),
):
    prompt = await get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail=f"Prompt not found: {prompt_id}")
    version = await get_version(db, prompt_id, version_number)
    if not version:
        raise HTTPException(status_code=404, detail=f"Version not found: {version_number}")
    return version


@router.post("/{version_number}/restore", response_model=PromptResponse)
async def restore_version_endpoint(
    prompt_id: str,
    version_number: int,
    db: aiosqlite.Connection = Depends(get_db),
):
    prompt = await get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail=f"Prompt not found: {prompt_id}")
    result = await restore_version(db, prompt_id, version_number)
    if not result:
        raise HTTPException(status_code=404, detail=f"Version not found: {version_number}")
    return result
