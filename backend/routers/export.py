"""익스포트/동기화 API 라우터."""

from pathlib import Path

from fastapi import APIRouter, Depends

import aiosqlite

from backend.database import get_db
from backend.models import ExportSummary
from backend.services.export_service import export_all_to_md, sync_meta_files

router = APIRouter(prefix="/api/export", tags=["export"])

PROJECT_ROOT = str(Path(__file__).parent.parent.parent)


@router.get("", response_model=ExportSummary)
async def export_prompts(db: aiosqlite.Connection = Depends(get_db)):
    """전체 프롬프트를 .md 파일로 익스포트한다."""
    return await export_all_to_md(db, PROJECT_ROOT)


@router.post("/sync", response_model=ExportSummary)
async def sync_files(db: aiosqlite.Connection = Depends(get_db)):
    """prompts.meta.yaml과 web/data.json을 재생성한다."""
    return await sync_meta_files(db, PROJECT_ROOT)
