"""AKShare 数据源封装"""
import akshare as ak
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

# 股票列表缓存
_stock_list_cache = None


def get_stock_list() -> pd.DataFrame:
    """获取 A 股全部股票实时行情 (带缓存)"""
    global _stock_list_cache
    if _stock_list_cache is not None:
        return _stock_list_cache

    df = ak.stock_zh_a_spot_em()
    # 只保留需要的列
    keep_cols = {
        '代码': 'code', '名称': 'name', '最新价': 'price',
        '涨跌幅': 'change_pct', '涨跌额': 'change',
        '成交量': 'volume', '成交额': 'turnover',
        '振幅': 'amplitude', '最高': 'high', '最低': 'low',
        '今开': 'open', '昨收': 'pre_close',
        '量比': 'vol_ratio', '换手率': 'turnover_rate',
        '市盈率-动态': 'pe', '市净率': 'pb',
        '总市值': 'total_mv', '流通市值': 'circ_mv',
    }
    df = df.rename(columns={k: v for k, v in keep_cols.items() if k in df.columns})
    df = df[list(keep_cols.values())]
    # 数值转换
    for col in ['price', 'change_pct', 'pe', 'pb', 'vol_ratio', 'turnover_rate']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    _stock_list_cache = df
    return df


def get_stock_info(code: str) -> dict:
    """获取个股基本信息"""
    info = ak.stock_individual_info_em(symbol=code)
    result = {}
    for _, row in info.iterrows():
        result[row['item']] = row['value']
    return result


def get_financial_data(code: str) -> dict:
    """获取财务指标 (ROE/毛利率/净利率/资产负债率等)"""
    try:
        df = ak.stock_financial_abstract_ths(symbol=code)
        if df is not None and len(df) > 0:
            return df.iloc[-1].to_dict()
    except Exception:
        pass
    return {}


def get_technical_indicators(code: str, period: str = 'daily') -> pd.DataFrame:
    """获取日线行情数据 (用于计算均线/MACD/RSI/BOLL)"""
    try:
        df = ak.stock_zh_a_hist(symbol=code, period=period, adjust='qfq')
        return df
    except Exception:
        return pd.DataFrame()


def get_capital_flow(code: str) -> dict:
    """获取资金流向"""
    try:
        df = ak.stock_individual_fund_flow(stock=code, market='sh')
        if df is not None and len(df) > 0:
            return df.iloc[-1].to_dict()
    except Exception:
        pass
    return {}
