"""完整分析流程 — L1过滤 → L2评分 → 板块分组
M7 优化: 并行评分 + 内存缓存
"""
import re
import time
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.data.akshare_client import (
    get_stock_list, get_stock_basic_info, get_stock_kline,
    get_stock_financials, get_market_overview
)
from app.engine.l1_filter import filter_stocks
from app.engine.l2_scorer import grade_stock
from app.engine.sector_heat import assign_sector, group_by_sector

# ========== 内存缓存 (单次分析生命周期) ==========
_cache = {}


def _get_cached(fn, key, *args, **kwargs):
    """带缓存的函数调用"""
    if key not in _cache:
        try:
            _cache[key] = fn(*args, **kwargs)
        except Exception as e:
            _cache[key] = None
    return _cache[key]


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
    """AKShare 中文财务 → 评分引擎英文格式"""
    if not raw:
        return {'roe': 0, 'profit_growth': 0, 'revenue_growth': 0,
                'gross_margin': 0, 'debt_ratio': 0, 'operating_cashflow': 0,
                'has_dividend': False, 'pe_percentile': 50}
    report_date = raw.get('报告期', '')
    quarter = 4
    if isinstance(report_date, str) and len(report_date) >= 7:
        month = int(report_date[5:7])
        if month <= 3: quarter = 1
        elif month <= 6: quarter = 2
        elif month <= 9: quarter = 3
    annualize = 4 / quarter if quarter < 4 else 1
    return {
        'roe': _parse_val(raw.get('净资产收益率', 0)) * annualize,
        'profit_growth': _parse_val(raw.get('净利润同比增长率', 0)) * annualize,
        'revenue_growth': _parse_val(raw.get('营业总收入同比增长率', 0)) * annualize,
        'gross_margin': _parse_val(raw.get('销售毛利率', 0)),
        'debt_ratio': _parse_val(raw.get('资产负债率', 0)),
        'operating_cashflow': _parse_val(raw.get('每股经营现金流', 0)) * annualize,
        'has_dividend': _parse_val(raw.get('基本每股收益', 0)) > 0,
        'pe_percentile': 50,
    }


def _clean(obj):
    if obj is None: return None
    if isinstance(obj, (np.bool_, np.integer)): return int(obj) if isinstance(obj, np.integer) else bool(obj)
    if isinstance(obj, np.floating): return float(obj)
    if isinstance(obj, np.ndarray): return obj.tolist()
    if isinstance(obj, dict): return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)): return [_clean(x) for x in obj]
    if isinstance(obj, pd.DataFrame): return obj.to_dict(orient='records')
    return obj


def _detect_board(code: str) -> str:
    if not code: return 'other'
    c = code.strip()
    if c.startswith('60') or c.startswith('00'): return 'main'
    if c.startswith('30'): return 'chinext'
    if c.startswith('68'): return 'star'
    if c.startswith(('8', '4')): return 'bse'
    return 'other'


def _score_single_stock(stock: dict) -> dict:
    """单只股票评分（用于并行执行）"""
    code = stock['code']
    name = stock['name']
    kline = _get_cached(get_stock_kline, f'kline_{code}', code, days=120)
    raw_fund = _get_cached(get_stock_financials, f'fund_{code}', code)
    fund = _map_fund(raw_fund)
    info = _get_cached(get_stock_basic_info, f'info_{code}', code)
    industry = info.get('行业', '') if info else ''
    # 确保 kline 是有效 DataFrame
    if kline is None or (isinstance(kline, pd.DataFrame) and kline.empty):
        kline = pd.DataFrame()
    r = grade_stock(code=code, name=name, fund_data=fund, kline=kline, cap_data={})
    r['sector'] = assign_sector(industry, name)
    r['industry'] = industry
    r['board'] = _detect_board(code)
    r['price'] = stock['price']
    r['change_pct'] = stock['change_pct']
    r['turnover'] = stock['turnover']
    return r


def run_full_analysis(progress_callback=None, max_workers=5, sample_size=None) -> dict:
    """
    完整选股流程 — M7 优化版
    max_workers: 并行线程数 (默认5, AKShare接口建议≤5)
    sample_size: 评分股票数量 (默认500, 前500只评分即可覆盖优质股)
    """
    global _cache
    _cache = {}  # 清空缓存
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
        if not code or not name: continue
        stock_list.append({
            'code': code, 'name': name,
            'price': row.get('最新价', 0),
            'change_pct': row.get('涨跌幅', 0),
            'turnover': row.get('成交额', 0),
        })
    result = filter_stocks(stock_list, {}, {}, {})
    passed = result['passed']
    rejected = result['rejected']
    log(f'L1 通过 {len(passed)}/{total} 只，排除 {len(rejected)} 只', 20)

    # ===== Step 3: L2 并行评分 =====
    if sample_size is None:
        sample_size = min(500, len(passed))  # 默认前500只（覆盖优质股）
    else:
        sample_size = min(sample_size, len(passed))

    log(f'L2 评分中 (前 {sample_size} 只, {max_workers}线程)...', 25)
    scored = []
    completed = 0
    batch_size = max(sample_size // 20, 1)  # 每5%更新一次进度

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_score_single_stock, s): s for s in passed[:sample_size]}
        for future in as_completed(futures):
            try:
                r = future.result()
                scored.append(r)
            except Exception as e:
                pass  # 跳过失败股票
            completed += 1
            if completed % batch_size == 0 or completed == sample_size:
                pct = 20 + int(completed / sample_size * 60)
                log(f'评分 {completed}/{sample_size}', pct)

    scored.sort(key=lambda x: x['total_score'], reverse=True)
    log('板块分组中...', 85)

    # ===== Step 4: 板块分组 =====
    sectors_all = group_by_sector(scored, top_n=6, per_sector=10)
    sectors_by_board = {}
    for board_key in ('main', 'chinext', 'star'):
        board_stocks = [s for s in scored if s.get('board') == board_key]
        sectors_by_board[board_key] = group_by_sector(board_stocks, top_n=6, per_sector=10)

    log('分析完成！', 100)
    elapsed = time.time() - t0

    stats = {
        'total': total, 'passed': len(passed), 'rejected': len(rejected),
        'A+': sum(1 for s in scored if s['rating'] == 'A+'),
        'A': sum(1 for s in scored if s['rating'] == 'A'),
        'B': sum(1 for s in scored if s['rating'] == 'B'),
        'C': sum(1 for s in scored if s['rating'] == 'C'),
    }
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
        'sectors': sectors_all, 'sectors_by_board': sectors_by_board,
        'stats': stats, 'board_stats': board_stats, 'elapsed': round(elapsed, 1),
    })
