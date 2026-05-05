"""首页数据 API"""
from fastapi import APIRouter
from app.models import DashboardData, SectorInfo, StockScore
from datetime import datetime

router = APIRouter()


@router.get("", response_model=DashboardData)
async def get_dashboard():
    """获取首页大盘数据 + 板块热度 + 统计信息"""
    # TODO: 实现真实数据获取
    return DashboardData(
        update_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
        sh_index=3350.25,
        sh_change=0.85,
        sz_index=10850.30,
        sz_change=1.12,
        cy_index=2180.50,
        cy_change=0.65,
        up_count=2850,
        down_count=2200,
        total_volume=1.25,
        sectors=[
            SectorInfo(name="科技", heat=92, change_pct=5.2, stock_count=10),
            SectorInfo(name="新能源", heat=78, change_pct=3.1, stock_count=10),
            SectorInfo(name="医药", heat=75, change_pct=-0.8, stock_count=10),
            SectorInfo(name="消费", heat=65, change_pct=1.5, stock_count=10),
            SectorInfo(name="金融", heat=60, change_pct=2.0, stock_count=10),
        ],
        stats={"A+": 12, "A": 28, "B": 35, "C": 15, "涨停": 85},
    )
