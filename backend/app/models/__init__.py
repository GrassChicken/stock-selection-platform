"""数据模型 - Pydantic schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class StockBasic(BaseModel):
    """股票基本信息"""
    code: str
    name: str
    industry: str = ""
    sector: str = ""


class StockScore(BaseModel):
    """股票评分数据"""
    code: str
    name: str
    price: float = 0
    change_pct: float = 0
    pe: float = 0
    pb: float = 0
    roe: float = 0
    gross_margin: float = 0
    debt_ratio: float = 0
    revenue_growth: float = 0
    profit_growth: float = 0
    operating_cashflow: float = 0
    has_dividend: bool = False
    fundamental_score: float = 0
    ma_bullish: bool = False
    macd_golden_cross: bool = False
    rsi: float = 50
    vol_ratio: float = 1.0
    price_above_ma20: bool = False
    technical_score: float = 0
    net_inflow_5d: float = 0
    margin_balance_up: bool = False
    rating_buy_ratio: float = 0
    capital_score: float = 0
    total_score: float = 0
    rating: str = "C"


class StockDetail(BaseModel):
    """个股详情（基本信息+评分明细）"""
    code: str
    name: str
    price: float = 0
    change_pct: float = 0
    industry: str = ""
    total_market_cap: float = 0
    float_market_cap: float = 0
    pe: float = 0
    pb: float = 0
    roe: float = 0
    gross_margin: float = 0
    debt_ratio: float = 0
    profit_growth: float = 0
    revenue_growth: float = 0
    operating_cashflow: float = 0
    has_dividend: bool = False
    fundamental_score: float = 0
    fundamental_details: dict = {}
    ma5: float = 0
    ma10: float = 0
    ma20: float = 0
    ma60: float = 0
    ma_bullish: bool = False
    macd_dif: float = 0
    macd_dea: float = 0
    macd_golden: bool = False
    rsi: float = 50
    vol_ratio: float = 1.0
    price_above_ma20: bool = False
    technical_score: float = 0
    technical_details: dict = {}
    net_inflow_5d: float = 0
    margin_balance_up: bool = False
    rating_buy_ratio: float = 0
    capital_score: float = 0
    capital_details: dict = {}
    total_score: float = 0
    rating: str = "C"


class StockTradePoints(BaseModel):
    """买卖点建议"""
    code: str
    name: str
    buy_range: str = ""
    sell_range: str = ""
    stop_profit: float = 0
    stop_loss: float = 0
    risk_reward_ratio: str = ""


class SectorInfo(BaseModel):
    """板块信息"""
    name: str
    heat: float = 0
    change_pct: float = 0
    stock_count: int = 0
    stocks: List[StockScore] = []


class DashboardData(BaseModel):
    """首页大盘数据"""
    update_time: str = ""
    sh_index: float = 0
    sh_change: float = 0
    sz_index: float = 0
    sz_change: float = 0
    cy_index: float = 0
    cy_change: float = 0
    up_count: int = 0
    down_count: int = 0
    total_volume: float = 0
    sectors: List[SectorInfo] = []
    stats: dict = {}


class AnalysisTask(BaseModel):
    """分析任务"""
    task_id: str
    trigger: str = "manual"
    status: str = "pending"
    progress: float = 0
    current_step: str = ""
    total_steps: int = 3
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    message: str = ""


class ScheduleConfig(BaseModel):
    """定时任务配置"""
    enabled: bool = True
    hour: int = 16
    minute: int = 0
    weekdays: List[int] = [0, 1, 2, 3, 4]
    notify_feishu: bool = True


class ScoringWeights(BaseModel):
    """评分权重配置"""
    fundamental: float = 50.0
    technical: float = 30.0
    capital: float = 20.0
