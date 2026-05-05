"""买卖点计算引擎"""


def calculate_trade_points(stock: dict) -> dict:
    """
    基于技术指标计算合理买卖价格区间
    stock: {price, ma20, ma60, boll_lower, boll_upper, recent_low, recent_high, ...}
    """
    price = stock.get('price', 0)
    if price <= 0:
        return {'error': '价格数据无效'}

    ma20 = stock.get('ma20', price * 0.97)
    ma60 = stock.get('ma60', price * 1.05)
    boll_lower = stock.get('boll_lower', price * 0.95)
    boll_upper = stock.get('boll_upper', price * 1.08)
    recent_low = stock.get('recent_low', price * 0.92)
    recent_high = stock.get('recent_high', price * 1.10)

    # 买入区间: 支撑位附近
    buy_support = max(ma20 * 0.98, boll_lower, recent_low * 1.02)

    # 卖出区间: 压力位附近
    sell_resistance = min(ma60 * 1.05, boll_upper, recent_high * 0.98)

    # 止盈止损
    stop_profit = price * 1.15  # 15%止盈
    stop_loss = price * 0.92    # 8%止损

    # 盈亏比
    rr = (sell_resistance - buy_support) / (buy_support - stop_loss) if buy_support > stop_loss else 0

    return {
        'buy_range': f"{buy_support:.2f} - {buy_support * 1.03:.2f}",
        'sell_range': f"{sell_resistance:.2f} - {sell_resistance * 1.03:.2f}",
        'stop_profit': round(stop_profit, 2),
        'stop_loss': round(stop_loss, 2),
        'risk_reward_ratio': f"{rr:.1f}:1",
    }
