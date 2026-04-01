"""Pydantic 모델 — 요청/응답 스키마."""

from pydantic import BaseModel


class PromptBase(BaseModel):
    title: str
    category: str
    content: str
    tags: list[str] = []
    role: str = ""


class PromptCreate(PromptBase):
    id: str | None = None


class PromptUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    role: str | None = None
    change_summary: str = ""


class PromptResponse(PromptBase):
    id: str
    type: str = "prompt"
    origin: str
    source: str
    file_path: str
    created_at: str
    updated_at: str


class PromptListItem(BaseModel):
    id: str
    title: str
    category: str
    tags: list[str]
    type: str = "prompt"
    role: str
    origin: str
    updated_at: str


class PromptListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    prompts: list[PromptListItem]


class VersionResponse(BaseModel):
    id: int
    prompt_id: str
    title: str
    content: str
    tags: list[str]
    version_number: int
    created_at: str
    change_summary: str


class ExportSummary(BaseModel):
    total_exported: int
    output_directory: str


class SuggestionCreate(BaseModel):
    prompt_id: str
    original_content: str
    suggested_content: str
    reason: str
    requested_by: str | None = None


class SuggestionResponse(BaseModel):
    id: int
    prompt_id: str
    original_content: str
    suggested_content: str
    reason: str
    status: str
    created_at: str
    resolved_at: str | None = None


class AIStatusResponse(BaseModel):
    available: bool


class ErrorResponse(BaseModel):
    detail: str
