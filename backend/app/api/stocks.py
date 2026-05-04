"""个股 API"""
from fastapi import APIRouter
from app.models import StockScore, StockTradePoints

router = APIRouter()


@router.get("/{code}", response_model=StockScore)
async def get_stock(code: str):
    """获取单只股票评分和指标数据"""
    # TODO: 实现真实数据
    return StockScore(
        code=code, name="示例股票", price=25.30, change_pct=1.5,
        pe=18.5, pb=2.3, roe=16.8, gross_margin=42.5,
        debt_ratio=35.2, revenue_growth=15.3, profit_growth=12.8,
        operating_cashflow=8.5, has_dividend=True,
        fundamental_score=42,
        ma_bullish=True, macd_golden_cross=True, rsi=55, vol_ratio=1.8,
        price_above_ma20=True, technical_score=25,
        net_inflow_5d=5200, margin_balance_up=True, rating_buy_ratio=0.65,
        capital_score=15, total_score=82, rating="A+",
    )


@router.get("/{code}/chart")
async def get_stock_chart(code: str):
    """获取 K 线数据"""
    # TODO: 实现真实 K 线数据
    return {"code": code, "klines": []}


@router.get("/{code}/trade-points", response_model=StockTradePoints)
async def get_trade_points(code: str):
    """获取买卖点建议"""
    # TODO: 实现真实计算
    return StockTradePoints(
        code=code, name="示例股票",
        buy_range="24.50 - 25.25",
        sell_range="27.80 - 28.60",
        stop_profit=29.10, stop_loss=23.28,
        risk_reward_ratio="3.2:1",
    )
