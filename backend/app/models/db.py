"""数据库模型"""
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import get_settings

Base = declarative_base()


class StockScore(Base):
    """股票评分记录"""
    __tablename__ = 'stock_scores'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), nullable=False, index=True)
    name = Column(String(50))
    analysis_date = Column(DateTime, nullable=False, index=True)

    # 基本面
    pe = Column(Float)
    pb = Column(Float)
    roe = Column(Float)
    gross_margin = Column(Float)
    debt_ratio = Column(Float)
    revenue_growth = Column(Float)
    profit_growth = Column(Float)
    operating_cashflow = Column(Float)
    has_dividend = Column(Boolean)
    fundamental_score = Column(Float)

    # 技术面
    ma5 = Column(Float)
    ma10 = Column(Float)
    ma20 = Column(Float)
    ma60 = Column(Float)
    ma_bullish = Column(Boolean)
    macd_dif = Column(Float)
    macd_dea = Column(Float)
    macd_hist = Column(Float)
    macd_golden = Column(Boolean)
    rsi = Column(Float)
    vol_ratio = Column(Float)
    technical_score = Column(Float)

    # 资金面
    main_net_inflow_5d = Column(Float)
    margin_balance_trend = Column(Float)
    rating_buy_pct = Column(Float)
    capital_score = Column(Float)

    # 综合
    total_score = Column(Float, index=True)
    rating = Column(String(2))

    # 详情
    fundamental_details = Column(JSON)
    technical_details = Column(JSON)
    technical_indicators = Column(JSON)
    capital_details = Column(JSON)


class AnalysisTask(Base):
    """分析任务记录"""
    __tablename__ = 'analysis_tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(50), unique=True, nullable=False)
    trigger = Column(String(20))  # manual / scheduled
    status = Column(String(20))  # pending / running / completed / failed
    progress = Column(Float)
    current_step = Column(String(100))
    total_steps = Column(Integer, default=3)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    message = Column(Text)


# 数据库初始化
_engine = None
_Session = None


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(settings.DB_URL, echo=False)
        Base.metadata.create_all(_engine)
    return _engine


def get_session():
    global _Session
    if _Session is None:
        engine = get_engine()
        _Session = sessionmaker(bind=engine)
    return _Session()
