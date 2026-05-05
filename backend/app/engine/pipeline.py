"""完整分析流程 — L1过滤 → L2评分 → 板块分组"""
import time
import pandas as pd
from app.data.akshare_client import (
    get_stock_list, get_stock_basic_info, get_stock_kline,
    get_stock_financials, get_market_overview
)
from app.engine.l1_filter import filter_stocks
from app.engine.l2_scorer import grade_stock
from app.engine.sector_heat import assign_sector, group_by_sector


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

        # 财务数据
        fund = get_stock_financials(code)

        # 行业 + 板块
        info = get_stock_basic_info(code)
        industry = info.get('行业', '')
        sector = assign_sector(industry, name)

        # 评分
        r = grade_stock(
            code=code, name=name,
            fund_data=fund,
            kline=kline,
            cap_data={},
        )
        r['sector'] = sector
        r['industry'] = industry
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
    sectors = group_by_sector(scored, top_n=6, per_sector=10)

    log('分析完成！', 100)

    elapsed = time.time() - t0

    stats = {
        'total': total,
        'passed': len(passed),
        'rejected': len(rejected),
        'A+': sum(1 for s in scored if s['rating'] == 'A+'),
        'A': sum(1 for s in scored if s['rating'] == 'A'),
        'B': sum(1 for s in scored if s['rating'] == 'B'),
        'C': sum(1 for s in scored if s['rating'] == 'C'),
    }

    return {
        'sectors': sectors,
        'stats': stats,
        'elapsed': round(elapsed, 1),
    }
