from __future__ import annotations

from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from .routers import action_items, notes
from .dependencies import get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    在应用启动时初始化数据库，关闭时进行清理
    """
    # 启动时初始化数据库
    logger.info("Initializing database...")
    db = get_db()  # 这会触发数据库初始化
    logger.info("Database initialized successfully")
    
    yield
    
    # 关闭时的清理工作（如果需要）
    logger.info("Application shutdown")


app = FastAPI(
    title="Action Item Extractor",
    description="从文本中提取行动项的 API 服务",
    version="2.0.0",
    lifespan=lifespan
)


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    """
    返回前端页面
    
    Returns:
        str: HTML 页面内容
    """
    html_path = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
    return html_path.read_text(encoding="utf-8")


# 注册路由
app.include_router(notes.router)
app.include_router(action_items.router)

# 挂载静态文件
static_dir = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")