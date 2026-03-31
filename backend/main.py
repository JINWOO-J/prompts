"""FastAPI 앱 엔트리포인트."""

from contextlib import asynccontextmanager
from pathlib import Path

_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from backend.database import init_db, DB_PATH
from backend.migrate import migrate_all
from backend.routers.prompts import router as prompts_router
from backend.routers.versions import router as versions_router
from backend.routers.export import router as export_router
from backend.routers.suggestions import router as suggestions_router

WEB_DIR = Path(__file__).parent.parent / "web"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # DB가 비어있으면 .md 파일에서 자동 마이그레이션
    import aiosqlite
    async with aiosqlite.connect(DB_PATH) as db:
        row = await db.execute_fetchall("SELECT COUNT(*) FROM prompts")
        if row[0][0] == 0:
            await migrate_all()
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
app.include_router(suggestions_router)

# 정적 파일 서빙 — API 라우터 뒤에 마운트하여 API 경로 우선
if WEB_DIR.exists():

    @app.get("/", response_class=HTMLResponse)
    async def serve_index():
        return (WEB_DIR / "index.html").read_text(encoding="utf-8")

    app.mount("/", StaticFiles(directory=str(WEB_DIR)), name="static")
