"""分析控制 API"""
from fastapi import APIRouter
import uuid
from datetime import datetime
from app.models import AnalysisTask

router = APIRouter()

# 内存存储任务状态 (Phase 1 改为数据库)
_tasks = {}


@router.post("/", response_model=AnalysisTask)
async def trigger_analysis(trigger: str = "manual"):
    """手动触发分析"""
    task_id = str(uuid.uuid4())[:8]
    task = AnalysisTask(
        task_id=task_id,
        trigger=trigger,
        status="pending",
        current_step="等待开始",
    )
    _tasks[task_id] = task
    # TODO: 后台异步执行 L1 -> L2 -> 板块分组
    return task


@router.get("/status/{task_id}", response_model=AnalysisTask)
async def get_analysis_status(task_id: str):
    """查询分析任务进度"""
    task = _tasks.get(task_id)
    if not task:
        return AnalysisTask(task_id=task_id, status="not_found", message="任务不存在")
    # TODO: 返回真实进度
    return task


@router.get("/history")
async def get_analysis_history():
    """查看历史分析记录"""
    # TODO: 从数据库读取
    return {"records": []}


@router.post("/ai/{code}")
async def ai_analyze_stock(code: str):
    """调用 LLM 生成个股深度报告"""
    # TODO: 实现 LLM 调用
    return {"code": code, "report": "深度分析报告待实现"}


@router.post("/ai/compare")
async def ai_compare_stocks(codes: str):
    """多只股票对比分析"""
    # TODO: 实现 LLM 对比分析
    return {"codes": codes.split(","), "report": "对比分析报告待实现"}
