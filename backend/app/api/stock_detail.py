"""个股详情 API — 基本信息 + 评分明细"""
from fastapi import APIRouter, HTTPException
from app.models import StockDetail
from app.data.akshare_client import get_stock_basic_info, get_stock_kline, get_stock_financials
from app.engine.l2_scorer import score_fundamental, score_technical, score_capital
from app.engine.pipeline import _map_fund, _detect_board
import pandas as pd
import numpy as np

router = APIRouter()


def _clean_val(v):
    if v is None: return 0.0
    if isinstance(v, (np.floating, np.integer)): return float(v)
    return float(v) if v else 0.0


def _safe_bool(v):
    if isinstance(v, (np.bool_, bool)): return bool(v)
    return False


def _get_score_detail(score, details, indicators):
    """提取评分明细"""
    result = {}
    for k, v in details.items():
        if isinstance(v, dict):
            result[k] = {
                'value': _clean_val(v.get('value', 0)),
                'score': _clean_val(v.get('score', 0)),
                'max': _clean_val(v.get('max', 0)),
            }
    for k, v in indicators.items():
        if isinstance(v, (bool, np.bool_)):
            result[k] = bool(v)
        else:
            result[k] = _clean_val(v)
    return result


@router.get("", response_model=StockDetail)
async def get_stock_detail(code: str):
    """
    获取个股详情：基本信息 + 完整评分明细
    
    用法: /api/stocks/detail?code=600519
    """
    if not code or len(code) < 4:
        raise HTTPException(status_code=400, detail="请输入有效的股票代码")

    # 基本信息
    info = get_stock_basic_info(code)
    if not info or not info.get('股票简称'):
        raise HTTPException(status_code=404, detail=f"未找到股票 {code}")

    name = info.get('股票简称', code)
    price = info.get('最新', 0)
    total_cap = info.get('总市值', 0)
    float_cap = info.get('流通市值', 0)

    # K线 + 技术指标
    kline = get_stock_kline(code, days=120)

    # 财务数据
    raw_fund = get_stock_financials(code)
    fund = _map_fund(raw_fund)

    # 评分
    fs, fd = score_fundamental(fund)
    ts, td, ti = score_technical(kline)
    cs, cd = score_capital({})

    # 技术指标值
    ma_vals = {
        'ma5': ti.get('ma5', 0), 'ma10': ti.get('ma10', 0),
        'ma20': ti.get('ma20', 0), 'ma60': ti.get('ma60', 0),
        'ma_bullish': _safe_bool(ti.get('ma_bullish', False)),
        'macd_dif': ti.get('macd_dif', 0), 'macd_dea': ti.get('macd_dea', 0),
        'macd_golden': _safe_bool(ti.get('macd_golden', False)),
        'rsi': ti.get('rsi', 50), 'vol_ratio': ti.get('vol_ratio', 1.0),
        'price_above_ma20': _safe_bool(ti.get('ma_bullish', False)),
    }

    total = fs + ts + cs
    if total >= 80: rating = 'A+'
    elif total >= 65: rating = 'A'
    elif total >= 50: rating = 'B'
    else: rating = 'C'

    return StockDetail(
        code=code, name=name, price=round(float(price), 2),
        change_pct=0,
        industry=info.get('行业', ''),
        total_market_cap=round(float(total_cap) / 1e8, 2) if total_cap else 0,
        float_market_cap=round(float(float_cap) / 1e8, 2) if float_cap else 0,
        pe=fund.get('pe', 0), pb=fund.get('pb', 0),
        roe=round(fund.get('roe', 0), 2),
        gross_margin=round(fund.get('gross_margin', 0), 2),
        debt_ratio=round(fund.get('debt_ratio', 0), 2),
        profit_growth=round(fund.get('profit_growth', 0), 2),
        revenue_growth=round(fund.get('revenue_growth', 0), 2),
        operating_cashflow=round(fund.get('operating_cashflow', 0), 2),
        has_dividend=fund.get('has_dividend', False),
        fundamental_score=fs,
        fundamental_details=_get_score_detail(fs, fd, {}),
        ma5=round(_clean_val(ma_vals['ma5']), 2),
        ma10=round(_clean_val(ma_vals['ma10']), 2),
        ma20=round(_clean_val(ma_vals['ma20']), 2),
        ma60=round(_clean_val(ma_vals['ma60']), 2),
        ma_bullish=ma_vals['ma_bullish'],
        macd_dif=round(_clean_val(ma_vals['macd_dif']), 3),
        macd_dea=round(_clean_val(ma_vals['macd_dea']), 3),
        macd_golden=ma_vals['macd_golden'],
        rsi=round(_clean_val(ma_vals['rsi']), 1),
        vol_ratio=round(_clean_val(ma_vals['vol_ratio']), 2),
        price_above_ma20=ma_vals['price_above_ma20'],
        technical_score=ts,
        technical_details=_get_score_detail(ts, td, ti),
        capital_score=cs,
        capital_details=_get_score_detail(cs, cd, {}),
        total_score=round(total, 1),
        rating=rating,
    )
