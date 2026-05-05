"""L1 一票否决过滤引擎"""


def is_st(name: str) -> bool:
    """判断是否为 ST 股票"""
    return 'ST' in name.upper() or '*ST' in name


def filter_stocks(stock_list: list, financials: dict = None,
                  corporate: dict = None, quotes: dict = None) -> dict:
    """
    L1 一票否决过滤
    Returns: {'passed': [stocks], 'rejected': {code: {name, reasons}}}
    """
    passed = []
    rejected = {}

    for stock in stock_list:
        code = stock.get('code', '')
        name = stock.get('name', '')
        reasons = []

        # 1. ST
        if is_st(name):
            reasons.append('ST/*ST 股票')

        # 2-4. 财务
        if financials and code in financials:
            f = financials[code]
            if f.get('net_profit', 0) < 0 and f.get('net_profit_prev', 0) < 0:
                reasons.append('近2年连续亏损')
            if f.get('operating_cashflow', 0) < 0 and f.get('operating_cashflow_prev', 0) < 0:
                reasons.append('经营现金流持续为负')
            dr = f.get('debt_ratio', 0)
            industry = f.get('industry', '')
            is_fin = any(x in industry for x in ['银行', '保险', '券商'])
            if dr > 0.80 and not is_fin:
                reasons.append(f'资产负债率过高 ({dr:.0%})')

        # 5-7. 公司治理
        if corporate and code in corporate:
            c = corporate[code]
            if c.get('has_penalty_recent', False):
                reasons.append('近1年被证监会处罚/立案')
            if c.get('pledge_ratio', 0) > 0.50:
                reasons.append(f'大股东质押过高 ({c["pledge_ratio"]:.0%})')
            if c.get('has_reduce_plan_recent', False):
                reasons.append('近3月有减持计划')

        # 8. 流动性
        if quotes and code in quotes:
            avg = quotes[code].get('avg_turnover_20d', float('inf'))
            if avg < 5_000_000:
                reasons.append(f'日均成交额过低 ({avg/1e4:.0f}万)')

        if reasons:
            rejected[code] = {'name': name, 'reasons': reasons}
        else:
            passed.append(stock)

    return {'passed': passed, 'rejected': rejected}
