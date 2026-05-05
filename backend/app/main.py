from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from app.config import get_settings
from app.api import dashboard, sectors, stocks, analyze, schedule, settings
from app.scheduler import init_scheduler, shutdown_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    settings = get_settings()
    init_scheduler()
    print(f"🦐 智能选股平台启动成功！")
    print(f"📍 访问地址: http://{settings.APP_HOST}:{settings.APP_PORT}")
    print(f"📚 API文档: http://{settings.APP_HOST}:{settings.APP_PORT}/api/docs")
    yield
    shutdown_scheduler()


app = FastAPI(
    title="智能选股平台",
    description="基于三层漏斗架构的A股智能选股系统",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["首页数据"])
app.include_router(sectors.router, prefix="/api/sectors", tags=["板块"])
app.include_router(stocks.router, prefix="/api/stocks", tags=["个股"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["分析控制"])
app.include_router(schedule.router, prefix="/api/schedule", tags=["定时任务"])
app.include_router(settings.router, prefix="/api/settings", tags=["系统设置"])


@app.get("/api/health", tags=["健康检查"])
async def health_check():
    return {"status": "ok", "message": "智能选股平台运行中 🦐"}


# 挂载前端静态文件
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend", "dist")
if os.path.exists(FRONTEND_DIST):
    # 挂载静态资源 (JS/CSS/Images)
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")
    
    # SPA 回退路由：非 /api 请求返回 index.html
    from fastapi.responses import HTMLResponse
    
    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        if full_path.startswith("api"):
            raise HTTPException(status_code=404)
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
    
    print(f"📁 前端静态文件已挂载: {FRONTEND_DIST}")
else:
    print(f"⚠️  前端静态文件目录不存在: {FRONTEND_DIST}")
