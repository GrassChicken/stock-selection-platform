"""首页数据 API — M2.1 接入真实引擎"""
from fastapi import APIRouter
from app.models import DashboardData
from app.data.akshare_client import get_market_overview
from datetime import datetime
import threading
import time

router = APIRouter()

# 行情快照缓存（首次触发后台刷新，不阻塞请求）
_market_cache: dict = {"data": None, "ts": 0}
_CACHE_TTL = 300  # 5分钟
_refresh_lock = threading.Lock()
_refresh_started = False


def _refresh_market_snapshot():
    """后台刷新行情快照"""
    try:
        from app.data.akshare_client import get_stock_list
        df = get_stock_list()
        if df is not None and not df.empty:
            _market_cache["data"] = {
                "up_count": int((df["涨跌幅"] > 0).sum()),
                "down_count": int((df["涨跌幅"] < 0).sum()),
                "flat_count": int((df["涨跌幅"] == 0).sum()),
                "total_volume": round(df["成交额"].sum() / 1e12, 2),  # 万亿
            }
            _market_cache["ts"] = time.time()
            print(f"📊 行情快照已更新: 涨{_market_cache['data']['up_count']} 跌{_market_cache['data']['down_count']} 成交额{_market_cache['data']['total_volume']}亿")
    except Exception as e:
        print(f"⚠️ 行情快照刷新失败: {e}")


def _ensure_background_refresh():
    """确保后台刷新线程已启动（只启动一次）"""
    global _refresh_started
    if _refresh_started:
        return
    with _refresh_lock:
        if _refresh_started:
            return
        _refresh_started = True
        threading.Thread(target=_refresh_market_snapshot, daemon=True).start()


def _get_latest_analysis_result():
    """获取最新分析结果（跨模块访问 analyze.py 的缓存）"""
    try:
        from app.api import analyze
        return getattr(analyze, '_latest_result', None)
    except Exception:
        return None


@router.get("", response_model=DashboardData)
async def get_dashboard():
    """获取首页大盘数据 + 板块热度 + 统计信息"""
    # 首次请求触发后台刷新（不阻塞当前响应）
    _ensure_background_refresh()

    result = DashboardData(
        update_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )

    # 1. 大盘指数（实时，轻量）
    market = get_market_overview()
    if market:
        sh = market.get("上证指数", {})
        sz = market.get("深证成指", {})
        cy = market.get("创业板指", {})

        def _float(v, default=0.0):
            try:
                return float(v)
            except (ValueError, TypeError):
                return default

        result.sh_index = _float(sh.get("最新价"), 0)
        result.sh_change = _float(sh.get("涨跌幅"), 0)
        result.sz_index = _float(sz.get("最新价"), 0)
        result.sz_change = _float(sz.get("涨跌幅"), 0)
        result.cy_index = _float(cy.get("最新价"), 0)
        result.cy_change = _float(cy.get("涨跌幅"), 0)

    # 2. 涨跌家数 + 成交额（后台缓存，有则返回，无则留空）
    snapshot = _market_cache.get("data")
    if snapshot:
        result.up_count = snapshot["up_count"]
        result.down_count = snapshot["down_count"]
        result.total_volume = snapshot["total_volume"]

    # 3. 分析结果（板块热度 + 统计 + board 统计）
    analysis = _get_latest_analysis_result()
    if analysis and not analysis.get("error"):
        sectors_raw = analysis.get("sectors", [])
        result.sectors = [
            {
                "name": s.get("name", ""),
                "heat": s.get("heat", 0),
                "change_pct": round(
                    sum(st.get("change_pct", 0) for st in s.get("stocks", []))
                    / max(len(s.get("stocks", [])), 1), 1
                ),
                "stock_count": len(s.get("stocks", [])),
                "stocks": s.get("stocks", []),
            }
            for s in sectors_raw
        ]
        # 合并 stats + board_stats
        stats = analysis.get("stats", {})
        stats["board_stats"] = analysis.get("board_stats", {})
        result.stats = stats
        result.update_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    return result
