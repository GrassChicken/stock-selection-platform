"""分析控制 API — 接入真实引擎 + 持久化存储"""
from fastapi import APIRouter
import uuid
import json
import os
from datetime import datetime
from app.models import AnalysisTask
from app.engine.pipeline import run_full_analysis

router = APIRouter()

# 内存存储任务状态
_tasks = {}
_latest_result = None

# 持久化存储路径
_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')
_CACHE_FILE = os.path.join(_CACHE_DIR, 'analysis_cache.json')


def _ensure_cache_dir():
    """确保缓存目录存在"""
    os.makedirs(_CACHE_DIR, exist_ok=True)


def save_result_to_disk(result):
    """保存分析结果到本地JSON"""
    try:
        _ensure_cache_dir()
        with open(_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"💾 分析结果已保存到: {_CACHE_FILE}")
    except Exception as e:
        print(f"⚠️ 保存分析结果失败: {e}")


def load_result_from_disk():
    """从本地JSON加载分析结果"""
    try:
        if os.path.exists(_CACHE_FILE):
            with open(_CACHE_FILE, 'r', encoding='utf-8') as f:
                result = json.load(f)
                print(f"📂 已加载缓存分析结果 (耗时{result.get('elapsed', 'N/A')}s)")
                return result
    except Exception as e:
        print(f"⚠️ 加载缓存失败: {e}")
    return None


# 启动时加载缓存
_loaded = load_result_from_disk()
if _loaded:
    _latest_result = _loaded


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
            # sample_size=500 确保只评前500只，避免超时
            _latest_result = run_full_analysis(progress_callback=progress, sample_size=500)
            # 持久化存储
            save_result_to_disk(_latest_result)
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
    """获取最新分析结果（内存优先，无则从磁盘加载）"""
    global _latest_result
    if _latest_result:
        return _latest_result
    # 内存没有，尝试从磁盘加载
    disk_result = load_result_from_disk()
    if disk_result:
        _latest_result = disk_result
        return _latest_result
    return {"message": "尚未执行分析"}


@router.get("/search")
async def search_stocks(q: str = ""):
    """搜索股票（代码/名称），从最新分析结果中查找"""
    if not q or len(q) < 1:
        return []
    # 确保加载了结果
    result = await get_latest_result()
    if result.get('message'):
        return []
    q = q.lower().strip()
    results = []
    seen = set()
    for sector in result.get('sectors', []):
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
    return {"code": code, "report": "深度分析报告待实现"}


@router.post("/ai/compare")
async def ai_compare_stocks(codes: str):
    """多只股票对比分析"""
    return {"codes": codes.split(","), "report": "对比分析报告待实现"}
