"""板块热度计算 + 分组"""


# 板块分类（申万一级行业 + 概念）
SECTORS = {
    '科技': ['半导体', '芯片', '通信设备', '计算机设备', '软件开发', '消费电子', '电子元件', '光学光电子', '算力租赁', 'AI'],
    '新能源': ['锂电池', '光伏设备', '风电设备', '储能', '新能源车', '电网设备'],
    '医药': ['化学制药', '中药', '生物制品', '医疗器械', '医疗服务', '医药商业'],
    '消费': ['白酒', '食品饮料', '家电', '零售', '旅游', '造纸', '农业'],
    '金融': ['银行', '保险', '证券', '多元金融'],
    '制造': ['军工', '通用设备', '机器人', '航空航天', '船舶', '轨交设备'],
    '周期': ['钢铁', '煤炭', '化工', '有色金属', '建材', '基础化工', '石油'],
    '地产基建': ['房地产', '建筑装饰', '建筑材料', '装修装饰', '物业管理'],
}


def assign_sector(industry: str, name: str = '') -> str:
    """根据行业名称/股票名称判断板块"""
    target = (industry or '') + (name or '')
    for sector, keywords in SECTORS.items():
        for kw in keywords:
            if kw in target:
                return sector
    return '其他'


def calculate_sector_heat(stocks_in_sector: list) -> float:
    """
    计算板块热度 (0-100)
    stocks_in_sector: [{change_pct, turnover, net_inflow, ...}, ...]
    """
    if not stocks_in_sector:
        return 0.0

    heat = 0.0

    # 1. 平均涨跌幅 (30分)
    changes = [s.get('change_pct', 0) for s in stocks_in_sector]
    avg = sum(changes) / len(changes)
    if avg > 3: heat += 30
    elif avg > 1: heat += 20
    elif avg > 0: heat += 10

    # 2. 涨停数量 (20分)
    limit_up = sum(1 for s in stocks_in_sector if s.get('change_pct', 0) >= 9.8)
    if limit_up >= 5: heat += 20
    elif limit_up >= 3: heat += 15
    elif limit_up >= 1: heat += 10

    # 3. 上涨占比 (15分)
    up = sum(1 for s in stocks_in_sector if s.get('change_pct', 0) > 0)
    ratio = up / len(stocks_in_sector) if stocks_in_sector else 0
    heat += ratio * 15

    # 4. 资金净流入 (15分)
    inflow = sum(s.get('net_inflow', 0) for s in stocks_in_sector)
    if inflow > 0: heat += 15

    # 5. 成交额占比 (20分)
    total_turnover = sum(s.get('turnover', 0) for s in stocks_in_sector)
    if total_turnover > 1e10: heat += 20
    elif total_turnover > 5e9: heat += 15
    elif total_turnover > 1e9: heat += 10

    return round(min(heat, 100), 1)


def group_by_sector(scored_stocks: list, top_n: int = 6, per_sector: int = 10) -> list:
    """
    按板块分组，每板块取 Top N，按热度排序取前 top_n 个板块
    """
    sectors = {}
    for stock in scored_stocks:
        sector = stock.get('sector', '其他')
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(stock)

    result = []
    for name, stocks in sectors.items():
        heat = calculate_sector_heat(stocks)
        top = sorted(stocks, key=lambda x: x.get('total_score', 0), reverse=True)[:per_sector]
        result.append({
            'name': name,
            'heat': heat,
            'stock_count': len(stocks),
            'stocks': top,
        })

    result.sort(key=lambda x: x['heat'], reverse=True)
    return result[:top_n]
