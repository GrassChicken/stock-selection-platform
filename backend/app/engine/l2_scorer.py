"""L2 量化评分引擎"""


def score_fundamental(stock: dict) -> float:
    """基本面评分 (0-50)"""
    score = 0
    if stock.get("roe", 0) > 0.15:
        score += 10
    if stock.get("profit_growth_3y", 0) > 0.10:
        score += 10
    if stock.get("pe_percentile", 1) < 0.4:
        score += 8
    if stock.get("operating_cashflow", 0) > 0:
        score += 7
    if stock.get("debt_ratio", 1) < 0.50:
        score += 7
    if stock.get("gross_margin", 0) > 0.30:
        score += 5
    if stock.get("has_dividend", False):
        score += 3
    return score


def score_technical(stock: dict) -> float:
    """技术面评分 (0-30)"""
    score = 0
    if stock.get("ma_bullish", False):
        score += 8
    if stock.get("macd_golden_cross", False):
        score += 7
    rsi = stock.get("rsi", 50)
    if 30 < rsi < 70:
        score += 5
    if stock.get("vol_ratio", 1) > 1.5:
        score += 5
    if stock.get("price_above_ma20", False):
        score += 5
    return score


def score_capital(stock: dict) -> float:
    """资金面评分 (0-20)"""
    score = 0
    if stock.get("net_inflow_5d", 0) > 0:
        score += 8
    if stock.get("margin_balance_up", False):
        score += 6
    if stock.get("rating_buy_ratio", 0) > 0.5:
        score += 6
    return score


def score_stock(stock: dict) -> dict:
    """对单只股票进行完整评分"""
    fs = score_fundamental(stock)
    ts = score_technical(stock)
    cs = score_capital(stock)
    total = fs * 0.50 + ts * 0.30 + cs * 0.20

    if total >= 80:
        rating = "A+"
    elif total >= 65:
        rating = "A"
    elif total >= 50:
        rating = "B"
    else:
        rating = "C"

    return {
        **stock,
        "fundamental_score": fs,
        "technical_score": ts,
        "capital_score": cs,
        "total_score": total,
        "rating": rating,
    }
