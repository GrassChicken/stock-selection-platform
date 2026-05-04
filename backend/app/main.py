from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.api import dashboard, sectors, stocks, analyze, schedule
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


@app.get("/api/health", tags=["健康检查"])
async def health_check():
    return {"status": "ok", "message": "智能选股平台运行中 🦐"}
