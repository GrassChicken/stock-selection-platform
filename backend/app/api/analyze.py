"""分析控制 API — 接入真实引擎"""
from fastapi import APIRouter
import uuid
from datetime import datetime
from app.models import AnalysisTask
from app.engine.pipeline import run_full_analysis

router = APIRouter()

# 内存存储任务状态 (Phase 1 改为数据库)
_tasks = {}
_latest_result = None


@router.post("", response_model=AnalysisTask)
async def trigger_analysis(trigger: str = "manual"):
    """手动触发分析"""
    task_id = str(uuid.uuid4())[:8]
    task = AnalysisTask(
        task_id=task_id,
        trigger=trigger,
        status="running",
        current_step="开始分析",
    )
    _tasks[task_id] = task

    # 后台执行分析
    def run():
        global _latest_result
        def progress(msg, pct):
            task.status = "running"
            task.current_step = msg
            task.progress = pct
        try:
            _latest_result = run_full_analysis(progress_callback=progress)
            task.status = "completed"
            task.progress = 100
            task.current_step = "分析完成"
            task.completed_at = datetime.now().isoformat()
        except Exception as e:
            task.status = "failed"
            task.message = str(e)

    import threading
    threading.Thread(target=run, daemon=True).start()

    return task


@router.get("/status/{task_id}", response_model=AnalysisTask)
async def get_analysis_status(task_id: str):
    """查询分析任务进度"""
    task = _tasks.get(task_id)
    if not task:
        return AnalysisTask(task_id=task_id, status="not_found", message="任务不存在")
    return task


@router.get("/history")
async def get_analysis_history():
    """查看历史分析记录"""
    return {"records": list(_tasks.values())}


@router.get("/latest")
async def get_latest_result():
    """获取最新分析结果"""
    global _latest_result
    if _latest_result:
        return _latest_result
    return {"message": "尚未执行分析"}


@router.get("/search")
async def search_stocks(q: str = ""):
    """搜索股票（代码/名称），从最新分析结果中查找"""
    if not q or len(q) < 1:
        return []
    global _latest_result
    if not _latest_result:
        return []
    q = q.lower().strip()
    results = []
    seen = set()
    for sector in _latest_result.get('sectors', []):
        for st in sector.get('stocks', []):
            code = str(st.get('code', ''))
            name = str(st.get('name', ''))
            key = code
            if key in seen: continue
            if q in code.lower() or q in name.lower():
                seen.add(key)
                results.append({
                    'code': code, 'name': name,
                    'price': st.get('price', 0),
                    'change_pct': st.get('change_pct', 0),
                    'total_score': st.get('total_score', 0),
                    'rating': st.get('rating', 'C'),
                    'sector': sector.get('name', ''),
                    'board': st.get('board', ''),
                })
            if len(results) >= 20:
                break
        if len(results) >= 20: break
    return results


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
