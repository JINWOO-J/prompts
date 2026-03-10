"""FastAPI 앱 엔트리포인트."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from backend.database import init_db
from backend.routers.prompts import router as prompts_router
from backend.routers.versions import router as versions_router
from backend.routers.export import router as export_router

WEB_DIR = Path(__file__).parent.parent / "web"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Prompt Management API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prompts_router)
app.include_router(versions_router)
app.include_router(export_router)

# 정적 파일 서빙 — API 라우터 뒤에 마운트하여 API 경로 우선
if WEB_DIR.exists():

    @app.get("/", response_class=HTMLResponse)
    async def serve_index():
        return (WEB_DIR / "index.html").read_text(encoding="utf-8")

    app.mount("/", StaticFiles(directory=str(WEB_DIR)), name="static")
