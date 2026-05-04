"""L3 LLM 深度分析引擎"""
from app.config import get_settings


def generate_stock_report(stock_data: dict) -> str:
    """
    调用大模型生成个股深度分析报告
    """
    settings = get_settings()
    # TODO: 实现真实 LLM 调用
    return f"对 {stock_data.get('code', '')} - {stock_data.get('name', '')} 的深度分析报告待实现"


def compare_stocks(stocks_data: list) -> str:
    """
    调用大模型对比多只股票
    """
    # TODO: 实现真实 LLM 对比分析
    return "股票对比分析报告待实现"
