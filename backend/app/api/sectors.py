"""板块 API — M2.3 接入真实分析结果"""
from fastapi import APIRouter
from typing import List
from app.models import SectorInfo, StockScore

router = APIRouter()


def _get_latest_analysis():
    """获取最新分析结果"""
    try:
        from app.api import analyze
        return getattr(analyze, '_latest_result', None)
    except Exception:
        return None


def _stock_to_score(st: dict) -> StockScore:
    """分析结果中的股票 dict → StockScore"""
    return StockScore(
        code=str(st.get('code', '')),
        name=str(st.get('name', '')),
        price=float(st.get('price', 0) or 0),
        change_pct=float(st.get('change_pct', 0) or 0),
        fundamental_score=float(st.get('fundamental_score', 0) or 0),
        technical_score=float(st.get('technical_score', 0) or 0),
        capital_score=float(st.get('capital_score', 0) or 0),
        total_score=float(st.get('total_score', 0) or 0),
        rating=str(st.get('rating', 'C')),
    )


@router.get("", response_model=List[SectorInfo])
async def get_sectors(board: str = ""):
    """获取所有板块列表及热度排名
    
    Args:
        board: 过滤板块 (main=主板, chinext=创业板, star=科创板)，空=全部
    """
    analysis = _get_latest_analysis()
    if analysis and not analysis.get('error'):
        # 按 board 过滤
        if board in ('main', 'chinext', 'star'):
            sectors_data = analysis.get('sectors_by_board', {}).get(board, [])
        else:
            sectors_data = analysis.get('sectors', [])
        return [
            SectorInfo(
                name=s.get('name', ''),
                heat=float(s.get('heat', 0) or 0),
                change_pct=round(
                    sum(st.get('change_pct', 0) for st in s.get('stocks', []))
                    / max(len(s.get('stocks', [])), 1), 1
                ),
                stock_count=len(s.get('stocks', [])),
                stocks=[_stock_to_score(st) for st in s.get('stocks', [])],
            )
            for s in sectors_data
        ]
    return []


@router.get("/{sector_name}/stocks", response_model=List[StockScore])
async def get_sector_stocks(sector_name: str):
    """获取指定板块 Top 10 股票列表"""
    analysis = _get_latest_analysis()
    if analysis and not analysis.get('error'):
        for s in analysis.get('sectors', []):
            if s.get('name') == sector_name:
                return [_stock_to_score(st) for st in s.get('stocks', [])]

    return []
