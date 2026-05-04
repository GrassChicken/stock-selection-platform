"""买卖点计算"""


def calculate_trade_points(stock: dict) -> dict:
    """
    基于技术指标计算合理买卖价格区间
    """
    price = stock.get("price", 0)
    ma20 = stock.get("ma20", price * 0.97)
    ma60 = stock.get("ma60", price * 1.05)
    boll_lower = stock.get("boll_lower", price * 0.95)
    boll_upper = stock.get("boll_upper", price * 1.08)
    recent_low = stock.get("recent_low", price * 0.92)
    recent_high = stock.get("recent_high", price * 1.10)

    buy_support = max(ma20 * 0.98, boll_lower, recent_low * 1.02)
    sell_resistance = min(ma60 * 1.05, boll_upper, recent_high * 0.98)
    stop_profit = price * 1.15
    stop_loss = price * 0.92

    rr = (sell_resistance - buy_support) / (buy_support - stop_loss) if buy_support > stop_loss else 0

    return {
        "code": stock.get("code", ""),
        "name": stock.get("name", ""),
        "buy_range": f"{buy_support:.2f} - {buy_support * 1.03:.2f}",
        "sell_range": f"{sell_resistance:.2f} - {sell_resistance * 1.03:.2f}",
        "stop_profit": round(stop_profit, 2),
        "stop_loss": round(stop_loss, 2),
        "risk_reward_ratio": f"{rr:.1f}:1",
    }
