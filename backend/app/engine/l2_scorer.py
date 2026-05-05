"""L2 量化评分引擎

评分体系（满分100分）：
  基本面 50分 + 技术面 30分 + 资金面 20分

技术指标：MA, MACD, RSI, BOLL, KDJ
"""

import pandas as pd
import numpy as np


# ============================================================
# 技术指标计算
# ============================================================

def calc_ma(series: pd.Series, window: int) -> pd.Series:
    """移动平均线"""
    return series.rolling(window=window).mean()


def calc_ema(series: pd.Series, span: int) -> pd.Series:
    """指数移动平均"""
    return series.ewm(span=span, adjust=False).mean()


def calc_macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    """MACD"""
    ema_fast = calc_ema(close, fast)
    ema_slow = calc_ema(close, slow)
    dif = ema_fast - ema_slow
    dea = calc_ema(dif, signal)
    macd = 2 * (dif - dea)
    return {'dif': dif, 'dea': dea, 'macd': macd}


def calc_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """RSI"""
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.inf)
    return 100 - (100 / (1 + rs))


def calc_boll(close: pd.Series, period: int = 20, num_std: float = 2.0) -> dict:
    """布林带"""
    mid = calc_ma(close, period)
    std = close.rolling(window=period).std()
    return {'upper': mid + num_std * std, 'mid': mid, 'lower': mid - num_std * std}


def calc_kdj(high: pd.Series, low: pd.Series, close: pd.Series, n: int = 9) -> dict:
    """KDJ"""
    lowest = low.rolling(window=n).min()
    highest = high.rolling(window=n).max()
    rsv = (close - lowest) / (highest - lowest).replace(0, np.inf) * 100
    k = rsv.ewm(com=2, adjust=False).mean()
    d = k.ewm(com=2, adjust=False).mean()
    j = 3 * k - 2 * d
    return {'k': k, 'd': d, 'j': j}


def calc_vol_ratio(volume: pd.Series, window: int = 5) -> float:
    """量比: 最近5日均量 / 20日均量"""
    if len(volume) < 20:
        return 1.0
    recent = volume.tail(window).mean()
    avg20 = volume.tail(20).mean()
    return recent / avg20 if avg20 > 0 else 1.0


# ============================================================
# 基本面评分 (0-50分)
# ============================================================

def score_fundamental(f: dict) -> tuple:
    """
    基本面评分
    f: {roe, profit_growth, revenue_growth, pe, pb, gross_margin,
        debt_ratio, operating_cashflow, has_dividend, ...}
    """
    score = 0
    details = {}

    # 1. ROE > 15% (10分)
    roe = f.get('roe', 0)
    if roe > 15: score += 10
    elif roe > 10: score += 5
    details['roe'] = {'value': round(roe, 2), 'score': min(score, 10), 'max': 10}

    # 2. 净利润增长率 > 10% (10分)
    pg = f.get('profit_growth', 0)
    if pg > 20: score += 10
    elif pg > 10: score += 7
    elif pg > 0: score += 3
    details['profit_growth'] = {'value': round(pg, 2), 'score': score - details['roe']['score'], 'max': 10}

    # 3. PE行业分位 (8分)
    pe_pct = f.get('pe_percentile', 50)
    s3 = 8 if pe_pct < 40 else (4 if pe_pct < 60 else 0)
    score += s3
    details['pe_pct'] = {'value': round(pe_pct, 1), 'score': s3, 'max': 8}

    # 4. 经营现金流 > 0 (7分)
    ocf = f.get('operating_cashflow', 0)
    s4 = 7 if ocf > 0 else 0
    score += s4
    details['ocf'] = {'value': round(ocf, 2), 'score': s4, 'max': 7}

    # 5. 资产负债率 < 50% (7分)
    dr = f.get('debt_ratio', 100)
    if dr < 50: score += 7
    elif dr < 70: score += 3
    details['debt'] = {'value': round(dr, 2), 'score': 7 if dr < 50 else (3 if dr < 70 else 0), 'max': 7}

    # 6. 毛利率 > 30% (5分)
    gm = f.get('gross_margin', 0)
    s6 = 5 if gm > 40 else (3 if gm > 20 else 0)
    score += s6
    details['gross_margin'] = {'value': round(gm, 2), 'score': s6, 'max': 5}

    # 7. 有分红 (3分)
    div = f.get('has_dividend', False)
    s7 = 3 if div else 0
    score += s7
    details['dividend'] = {'value': div, 'score': s7, 'max': 3}

    return score, details


# ============================================================
# 技术面评分 (0-30分)
# ============================================================

def score_technical(kline: pd.DataFrame) -> tuple:
    """
    技术面评分
    kline: DataFrame with [close, high, low, volume], 按日期升序
    """
    score = 0
    details = {}
    indicators = {}

    if kline is None or len(kline) < 60:
        return 0, {'error': '数据不足'}, {}

    close = kline['close']
    high = kline.get('high', close)
    low = kline.get('low', close)
    volume = kline.get('volume', pd.Series(dtype=float))
    price = close.iloc[-1]

    # 1. 均线多头排列 (8分)
    ma5 = calc_ma(close, 5).iloc[-1]
    ma10 = calc_ma(close, 10).iloc[-1]
    ma20 = calc_ma(close, 20).iloc[-1]
    ma60 = calc_ma(close, 60).iloc[-1]
    bullish = bool(ma5 > ma10 > ma20 > ma60)
    s1 = 8 if bullish else (4 if price > ma20 else 0)
    score += s1
    details['ma'] = {'bullish': bullish, 'score': s1, 'max': 8}
    indicators.update({'ma5': round(ma5, 2), 'ma10': round(ma10, 2),
                       'ma20': round(ma20, 2), 'ma60': round(ma60, 2),
                       'ma_bullish': bullish})

    # 2. MACD金叉 (7分)
    macd = calc_macd(close)
    dif = macd['dif'].iloc[-1]
    dea = macd['dea'].iloc[-1]
    hist = macd['macd'].iloc[-1]
    hist_prev = macd['macd'].iloc[-2] if len(macd['macd']) > 1 else 0
    golden = bool(dif > dea and hist > hist_prev and hist > 0)
    s2 = 7 if golden else 0
    score += s2
    details['macd'] = {'golden': golden, 'dif': round(dif, 3),
                       'dea': round(dea, 3), 'hist': round(hist, 3),
                       'score': s2, 'max': 7}
    indicators.update({'macd_dif': round(dif, 3), 'macd_dea': round(dea, 3),
                       'macd_hist': round(hist, 3), 'macd_golden': golden})

    # 3. RSI健康区间 (5分)
    rsi = calc_rsi(close).iloc[-1]
    healthy = 30 < rsi < 70
    s3 = 5 if healthy else (2 if rsi <= 30 else 0)
    score += s3
    details['rsi'] = {'value': round(rsi, 1), 'healthy': healthy, 'score': s3, 'max': 5}
    indicators['rsi'] = round(rsi, 1)

    # 4. 量比 (5分)
    vr = calc_vol_ratio(volume)
    s4 = 5 if vr > 1.5 else (2 if vr > 1 else 0)
    score += s4
    details['vol_ratio'] = {'value': round(vr, 2), 'score': s4, 'max': 5}
    indicators['vol_ratio'] = round(vr, 2)

    # 5. 站上MA20 (5分)
    above = bool(price > ma20)
    s5 = 5 if above else 0
    score += s5
    details['above_ma20'] = {'value': above, 'score': s5, 'max': 5}

    return score, details, indicators


# ============================================================
# 资金面评分 (0-20分)
# ============================================================

def score_capital(c: dict) -> tuple:
    """
    资金面评分
    c: {main_net_inflow_5d, margin_balance_trend, rating_buy_pct}
    """
    score = 0
    details = {}

    # 1. 主力近5日净流入 (8分)
    inflow = c.get('main_net_inflow_5d', 0)
    s1 = 8 if inflow > 0 else 0
    score += s1
    details['main_inflow'] = {'value': round(inflow / 1e4, 0), 'score': s1, 'max': 8}

    # 2. 融资余额趋势 (6分)
    trend = c.get('margin_balance_trend', 0)
    s2 = 6 if trend > 0 else (3 if trend == 0 else 0)
    score += s2
    details['margin'] = {'value': trend, 'score': s2, 'max': 6}

    # 3. 机构买入评级占比 (6分)
    pct = c.get('rating_buy_pct', 0)
    s3 = 6 if pct > 0.5 else (3 if pct > 0.3 else 0)
    score += s3
    details['rating'] = {'value': round(pct * 100, 1), 'score': s3, 'max': 6}

    return score, details


# ============================================================
# 综合评分 + 评级
# ============================================================

def grade_stock(code: str, name: str, fund_data: dict, kline: pd.DataFrame,
                cap_data: dict) -> dict:
    """对单只股票进行完整评分"""
    fs, fd = score_fundamental(fund_data)
    ts, td, ti = score_technical(kline)
    cs, cd = score_capital(cap_data)

    # 三项分数已经按权重分配了分值（基本面满分50 + 技术面满分30 + 资金面满分20 = 100）
    # 直接相加即可，不需要再乘权重！
    total = fs + ts + cs

    if total >= 80: rating = 'A+'
    elif total >= 65: rating = 'A'
    elif total >= 50: rating = 'B'
    else: rating = 'C'

    return {
        'code': code, 'name': name,
        'fundamental_score': fs, 'technical_score': ts, 'capital_score': cs,
        'total_score': round(total, 1), 'rating': rating,
        'fundamental_details': fd,
        'technical_details': td,
        'technical_indicators': ti,
        'capital_details': cd,
    }


def batch_grade(stocks: list) -> list:
    """批量评分
    stocks: [{code, name, fundamentals, kline, capital}, ...]
    """
    results = []
    for s in stocks:
        r = grade_stock(
            code=s['code'], name=s['name'],
            fund_data=s.get('fundamentals', {}),
            kline=s.get('kline', pd.DataFrame()),
            cap_data=s.get('capital', {}),
        )
        results.append(r)
    results.sort(key=lambda x: x['total_score'], reverse=True)
    return results
