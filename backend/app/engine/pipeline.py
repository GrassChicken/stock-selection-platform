"""完整分析流程 — L1过滤 → L2评分 → 板块分组"""
import re
import time
import numpy as np
import pandas as pd
from app.data.akshare_client import (
    get_stock_list, get_stock_basic_info, get_stock_kline,
    get_stock_financials, get_market_overview
)
from app.engine.l1_filter import filter_stocks
from app.engine.l2_scorer import grade_stock
from app.engine.sector_heat import assign_sector, group_by_sector


# ========== 财务字段映射 ==========
_FIN_MAP = {
    '净资产收益率': 'roe',
    '净利润同比增长率': 'profit_growth',
    '营业总收入同比增长率': 'revenue_growth',
    '销售毛利率': 'gross_margin',
    '资产负债率': 'debt_ratio',
    '每股经营现金流': 'operating_cashflow',
    '基本每股收益': 'eps',
}


def _parse_val(v) -> float:
    if isinstance(v, (int, float, np.number)):
        return float(v)
    if v is None:
        return 0.0
    s = str(v).strip()
    m = re.search(r'([\d.]+)%', s)
    if m:
        return float(m.group(1))
    m = re.search(r'([\d.]+)', s)
    if m:
        val = float(m.group(1))
        if '亿' in s:
            val *= 1e8
        elif '万' in s:
            val *= 1e4
        return val
    return 0.0


def _map_fund(raw: dict) -> dict:
    """AKShare 中文财务 → 评分引擎英文格式
    
    同花顺财务摘要的 ROE 是"加权净资产收益率"，已是年度化可比数据，
    但 Q1/Q3 累计值仍需年化。简化处理：根据报告期季度数估算年化。
    """
    report_date = raw.get('报告期', '')
    quarter = 4  # 默认按年度
    if isinstance(report_date, str) and len(report_date) >= 7:
        month = int(report_date[5:7])
        if month <= 3:
            quarter = 1
        elif month <= 6:
            quarter = 2
        elif month <= 9:
            quarter = 3
    
    annualize = 4 / quarter if quarter < 4 else 1  # Q1=4x, Q2=2x, Q3=1.33x, Q4=1x
    
    result = {}
    result['roe'] = _parse_val(raw.get('净资产收益率', 0)) * annualize
    result['profit_growth'] = _parse_val(raw.get('净利润同比增长率', 0))
    result['revenue_growth'] = _parse_val(raw.get('营业总收入同比增长率', 0))
    result['gross_margin'] = _parse_val(raw.get('销售毛利率', 0))
    result['debt_ratio'] = _parse_val(raw.get('资产负债率', 0))
    result['operating_cashflow'] = _parse_val(raw.get('每股经营现金流', 0)) * annualize
    result['has_dividend'] = _parse_val(raw.get('基本每股收益', 0)) > 0
    result['pe_percentile'] = 50
    return result


def _clean(obj):
    """递归转换 numpy/pandas 类型为 Python 原生类型"""
    if obj is None:
        return None
    if isinstance(obj, (np.bool_, np.integer)):
        return int(obj) if isinstance(obj, np.integer) else bool(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_clean(x) for x in obj]
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient='records')
    return obj


def _detect_board(code: str) -> str:
    """按股票代码判断所属板块"""
    if not code:
        return 'other'
    c = code.strip()
    if c.startswith('60'):
        return 'main'       # 沪市主板
    if c.startswith('00'):
        return 'main'       # 深市主板
    if c.startswith('30'):
        return 'chinext'    # 创业板
    if c.startswith('68'):
        return 'star'       # 科创板
    if c.startswith(('8', '4')):
        return 'bse'        # 北交所
    return 'other'


def run_full_analysis(progress_callback=None) -> dict:
    """
    完整选股流程
    progress_callback: callable(msg, pct)
    Returns: {sectors, stats, elapsed, error?}
    """
    t0 = time.time()

    def log(msg, pct):
        if progress_callback:
            progress_callback(msg, pct)

    # ===== Step 1: 获取全量股票 =====
    log('获取 A 股列表...', 5)
    df = get_stock_list()
    if df is None or df.empty:
        return {'error': '获取股票列表失败'}

    total = len(df)
    log(f'获取到 {total} 只股票', 10)

    # ===== Step 2: L1 一票否决 =====
    log('L1 过滤中...', 15)
    stock_list = []
    for _, row in df.iterrows():
        code = str(row.get('代码', '')).strip()
        name = str(row.get('名称', '')).strip()
        if not code or not name:
            continue
        stock_list.append({
            'code': code,
            'name': name,
            'price': row.get('最新价', 0),
            'change_pct': row.get('涨跌幅', 0),
            'turnover': row.get('成交额', 0),
        })

    # TODO: 批量获取财务/治理/流动性数据
    financials = {}
    corporate = {}
    quotes = {}

    result = filter_stocks(stock_list, financials, corporate, quotes)
    passed = result['passed']
    rejected = result['rejected']

    log(f'L1 通过 {len(passed)}/{total} 只，排除 {len(rejected)} 只', 20)

    # ===== Step 3: L2 评分 =====
    scored = []
    sample_size = min(100, len(passed))  # 先取100只测试

    log(f'L2 评分中 (前 {sample_size} 只)...', 25)

    for i, stock in enumerate(passed[:sample_size]):
        code = stock['code']
        name = stock['name']

        # K线数据
        kline = get_stock_kline(code, days=120)

        # 财务数据 + 字段映射
        raw_fund = get_stock_financials(code)
        fund = _map_fund(raw_fund)

        # 行业 + 板块
        info = get_stock_basic_info(code)
        industry = info.get('行业', '')
        sector = assign_sector(industry, name)
        board = _detect_board(code)  # 主板/创业板/科创板

        # 评分
        r = grade_stock(
            code=code, name=name,
            fund_data=fund,
            kline=kline,
            cap_data={},
        )
        r['sector'] = sector
        r['industry'] = industry
        r['board'] = board
        r['price'] = stock['price']
        r['change_pct'] = stock['change_pct']
        r['turnover'] = stock['turnover']
        scored.append(r)

        if (i + 1) % 20 == 0:
            pct = 20 + int((i + 1) / sample_size * 60)
            log(f'评分 {i+1}/{sample_size}', pct)

    scored.sort(key=lambda x: x['total_score'], reverse=True)

    log('板块分组中...', 85)

    # ===== Step 4: 板块分组 =====
    # 总体分组
    sectors_all = group_by_sector(scored, top_n=6, per_sector=10)
    # 分 board 分组
    sectors_by_board = {}
    for board_key in ('main', 'chinext', 'star'):
        board_stocks = [s for s in scored if s.get('board') == board_key]
        sectors_by_board[board_key] = group_by_sector(board_stocks, top_n=6, per_sector=10)

    log('分析完成！', 100)

    elapsed = time.time() - t0

    # 总体统计
    stats = {
        'total': total,
        'passed': len(passed),
        'rejected': len(rejected),
        'A+': sum(1 for s in scored if s['rating'] == 'A+'),
        'A': sum(1 for s in scored if s['rating'] == 'A'),
        'B': sum(1 for s in scored if s['rating'] == 'B'),
        'C': sum(1 for s in scored if s['rating'] == 'C'),
    }
    # 分 board 统计
    board_stats = {}
    for bk in ('main', 'chinext', 'star'):
        bs = [s for s in scored if s.get('board') == bk]
        board_stats[bk] = {
            'count': len(bs),
            'A+': sum(1 for s in bs if s['rating'] == 'A+'),
            'A': sum(1 for s in bs if s['rating'] == 'A'),
            'B': sum(1 for s in bs if s['rating'] == 'B'),
            'C': sum(1 for s in bs if s['rating'] == 'C'),
        }

    return _clean({
        'sectors': sectors_all,
        'sectors_by_board': sectors_by_board,
        'stats': stats,
        'board_stats': board_stats,
        'elapsed': round(elapsed, 1),
    })
