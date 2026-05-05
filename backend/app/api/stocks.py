"""个股 API — M2.2 接入真实评分引擎"""
from fastapi import APIRouter
from app.models import StockScore, StockTradePoints
from app.data.akshare_client import (
    get_stock_basic_info, get_stock_kline, get_stock_financials,
    get_stock_fund_flow
)
from app.engine.l2_scorer import grade_stock
from app.engine.trade_points import calculate_trade_points
import re
import numpy as np

router = APIRouter()


def _parse_value(v) -> float:
    """解析 AKShare 返回的字符串值（如 '10.57%', '272.43亿'）"""
    if isinstance(v, (int, float, np.number)):
        return float(v)
    if v is None:
        return 0.0
    s = str(v).strip()
    # 百分数
    m = re.search(r'([\d.]+)%', s)
    if m:
        return float(m.group(1))
    # 带单位的数字 (亿/万)
    m = re.search(r'([\d.]+)', s)
    if m:
        val = float(m.group(1))
        if '亿' in s:
            val *= 1e8
        elif '万' in s:
            val *= 1e4
        return val
    return 0.0


def _map_financials(raw: dict) -> dict:
    """将 AKShare 财务字段映射为评分引擎所需格式"""
    return {
        'roe': _parse_value(raw.get('净资产收益率', 0)),
        'profit_growth': _parse_value(raw.get('净利润同比增长率', 0)),
        'revenue_growth': _parse_value(raw.get('营业总收入同比增长率', 0)),
        'gross_margin': _parse_value(raw.get('销售毛利率', 0)),
        'debt_ratio': _parse_value(raw.get('资产负债率', 0)),
        'operating_cashflow': _parse_value(raw.get('每股经营现金流', 0)),
        'has_dividend': _parse_value(raw.get('基本每股收益', 0)) > 0,
        'pe': 0,        # TODO: 需要额外接口
        'pb': 0,
        'pe_percentile': 50,
    }


def _map_kline_indicators(ti: dict) -> dict:
    """将技术指标转换为前端可用格式"""
    return {
        'ma_bullish': bool(ti.get('ma_bullish', False)),
        'macd_golden_cross': bool(ti.get('macd_golden', False)),
        'rsi': float(ti.get('rsi', 50)),
        'vol_ratio': float(ti.get('vol_ratio', 1.0)),
        'price_above_ma20': bool(ti.get('ma_bullish', False)),
    }


@router.get("/{code}", response_model=StockScore)
async def get_stock(code: str):
    """获取单只股票评分和指标数据（实时计算）"""
    # 基本信息 + 价格（优先用 basic_info，避免拉全量行情）
    info = get_stock_basic_info(code)
    name = info.get('股票简称', code)
    price = info.get('最新', 0)
    change_pct = 0.0

    # K 线 + 技术指标
    kline = get_stock_kline(code, days=120)

    # 财务数据
    raw_fin = get_stock_financials(code)
    fund = _map_financials(raw_fin)
    fund['pe'] = _parse_value(info.get('市盈率', 0))
    fund['pb'] = _parse_value(info.get('市净率', 0))

    # 资金面（简化）
    cap = {}
    try:
        flow = get_stock_fund_flow(code)
        cap['main_net_inflow_5d'] = _parse_value(flow.get('主力净流入-净额', 0))
    except Exception:
        pass

    # 评分
    r = grade_stock(code=code, name=name, fund_data=fund, kline=kline, cap_data=cap)

    ti = _map_kline_indicators(r.get('technical_indicators', {}))

    return StockScore(
        code=code,
        name=name,
        price=round(float(price), 2),
        change_pct=round(float(change_pct), 2),
        pe=float(fund.get('pe', 0) or 0),
        pb=float(fund.get('pb', 0) or 0),
        roe=float(fund.get('roe', 0) or 0),
        gross_margin=float(fund.get('gross_margin', 0) or 0),
        debt_ratio=float(fund.get('debt_ratio', 0) or 0),
        revenue_growth=float(fund.get('revenue_growth', 0) or 0),
        profit_growth=float(fund.get('profit_growth', 0) or 0),
        operating_cashflow=float(fund.get('operating_cashflow', 0) or 0),
        has_dividend=bool(fund.get('has_dividend', False)),
        fundamental_score=float(r.get('fundamental_score', 0) or 0),
        ma_bullish=bool(ti.get('ma_bullish', False)),
        macd_golden_cross=bool(ti.get('macd_golden_cross', False)),
        rsi=float(ti.get('rsi', 50) or 50),
        vol_ratio=float(ti.get('vol_ratio', 1.0) or 1.0),
        price_above_ma20=bool(ti.get('price_above_ma20', False)),
        technical_score=float(r.get('technical_score', 0) or 0),
        net_inflow_5d=float(cap.get('main_net_inflow_5d', 0) or 0),
        margin_balance_up=False,
        rating_buy_ratio=0.5,
        capital_score=float(r.get('capital_score', 0) or 0),
        total_score=float(r.get('total_score', 0) or 0),
        rating=str(r.get('rating', 'C')),
    )


@router.get("/{code}/chart")
async def get_stock_chart(code: str):
    """获取 K 线数据（ECharts 格式）"""
    kline = get_stock_kline(code, days=120)
    if kline is None or kline.empty:
        return {"code": code, "dates": [], "klines": []}

    dates = kline.get('日期', kline.index).tolist()
    data = []
    for _, row in kline.iterrows():
        data.append([
            round(float(row.get('open', 0)), 2),
            round(float(row.get('close', 0)), 2),
            round(float(row.get('low', 0)), 2),
            round(float(row.get('high', 0)), 2),
        ])

    return {"code": code, "dates": [str(d) for d in dates], "klines": data}


@router.get("/{code}/trade-points", response_model=StockTradePoints)
async def get_trade_points(code: str):
    """获取买卖点建议"""
    info = get_stock_basic_info(code)
    price = info.get('最新', 0)
    name = info.get('股票简称', code)

    kline = get_stock_kline(code, days=120)
    if kline is None or kline.empty:
        return StockTradePoints(code=code, name=name)

    close = kline.get('close', kline.iloc[:, 0])
    high = kline.get('high', close)
    low = kline.get('low', close)

    from app.engine.l2_scorer import calc_ma, calc_boll
    ma20 = float(calc_ma(close, 20).iloc[-1])
    ma60 = float(calc_ma(close, 60).iloc[-1]) if len(close) >= 60 else ma20
    boll = calc_boll(close)
    boll_lower = float(boll['lower'].iloc[-1])
    boll_upper = float(boll['upper'].iloc[-1])
    recent_low = float(low.tail(20).min())
    recent_high = float(high.tail(20).max())

    tp = calculate_trade_points({
        'price': price,
        'ma20': ma20,
        'ma60': ma60,
        'boll_lower': boll_lower,
        'boll_upper': boll_upper,
        'recent_low': recent_low,
        'recent_high': recent_high,
    })

    return StockTradePoints(
        code=code,
        name=name,
        buy_range=tp.get('buy_range', ''),
        sell_range=tp.get('sell_range', ''),
        stop_profit=tp.get('stop_profit', 0),
        stop_loss=tp.get('stop_loss', 0),
        risk_reward_ratio=tp.get('risk_reward_ratio', ''),
    )
