"""AKShare 数据源封装"""
import akshare as ak
import pandas as pd
import warnings

warnings.filterwarnings('ignore')


def get_stock_list() -> pd.DataFrame:
    """获取 A 股全部股票实时行情 (东方财富接口)"""
    try:
        df = ak.stock_zh_a_spot_em()
        return df
    except Exception as e:
        print(f"⚠️ 获取股票列表失败: {e}")
        return pd.DataFrame()


def get_stock_basic_info(code: str) -> dict:
    """获取个股基本信息 (行业/市值/上市时间等)"""
    try:
        info = ak.stock_individual_info_em(symbol=code)
        result = {}
        for _, row in info.iterrows():
            result[row['item']] = row['value']
        return result
    except Exception:
        return {}


def get_stock_financials(code: str) -> dict:
    """获取财务摘要 (ROE/毛利率/净利率/资产负债率等)"""
    try:
        df = ak.stock_financial_abstract_ths(symbol=code)
        if df is not None and len(df) > 0:
            latest = df.iloc[-1].to_dict()
            return latest
    except Exception:
        pass
    return {}


def get_stock_kline(code: str, period: str = "daily", days: int = 120) -> pd.DataFrame:
    """获取个股日 K 线数据 (用于计算技术指标)"""
    try:
        df = ak.stock_zh_a_hist(symbol=code, period=period, adjust="qfq")
        if df is None or df.empty:
            return pd.DataFrame()
        # 只保留最近 N 天
        df = df.tail(days).copy()
        # 列名统一映射为英文，方便评分引擎使用
        col_map = {'开盘': 'open', '收盘': 'close', '最高': 'high',
                   '最低': 'low', '成交量': 'volume', '成交额': 'turnover',
                   '涨跌幅': 'change_pct', '换手率': 'turnover_rate'}
        df = df.rename(columns=col_map)
        return df
    except Exception:
        return pd.DataFrame()


def get_stock_fund_flow(code: str) -> dict:
    """获取个股资金流向 (东方财富)"""
    try:
        # 获取个股资金流历史
        df = ak.stock_individual_fund_flow(stock=code, market="sh")
        if df is not None and len(df) > 0:
            return df.iloc[-1].to_dict()
    except Exception:
        # 尝试深市
        try:
            df = ak.stock_individual_fund_flow(stock=code, market="sz")
            if df is not None and len(df) > 0:
                return df.iloc[-1].to_dict()
        except Exception:
            pass
    return {}


def get_sector_list() -> dict:
    """获取板块列表"""
    try:
        # 东方财富行业板块
        df = ak.stock_board_industry_name_em()
        return df
    except Exception:
        return pd.DataFrame()


def get_sector_stocks(sector_name: str) -> pd.DataFrame:
    """获取某板块的成分股"""
    try:
        df = ak.stock_board_industry_cons_em(symbol=sector_name)
        return df
    except Exception:
        return pd.DataFrame()


def get_market_overview() -> dict:
    """获取大盘指数概况（上证+深证+创业板）"""
    result = {}
    try:
        # 上证指数（从东方财富指数列表获取，快速）
        df = ak.stock_zh_index_spot_em()
        for _, row in df.iterrows():
            if row.get("名称") == "上证指数":
                result["上证指数"] = row.to_dict()
                break
    except Exception:
        pass

    # 深证成指 + 创业板指（逐条拉取，轻量）
    for code, name in [("399001", "深证成指"), ("399006", "创业板指")]:
        try:
            df = ak.stock_zh_index_daily(symbol=f"sz{code}")
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                prev = df.iloc[-2] if len(df) > 1 else latest
                change_pct = round(
                    (latest["close"] - prev["close"]) / prev["close"] * 100, 2
                ) if prev["close"] != 0 else 0
                result[name] = {
                    "最新价": round(latest["close"], 2),
                    "涨跌幅": change_pct,
                }
        except Exception:
            pass

    return result
