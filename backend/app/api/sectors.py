"""板块 API"""
from fastapi import APIRouter
from typing import List
from app.models import SectorInfo, StockScore

router = APIRouter()


@router.get("", response_model=List[SectorInfo])
async def get_sectors():
    """获取所有板块列表及热度排名"""
    # TODO: 实现真实数据
    return [
        SectorInfo(name="科技", heat=92, change_pct=5.2, stock_count=10),
        SectorInfo(name="新能源", heat=78, change_pct=3.1, stock_count=10),
        SectorInfo(name="医药", heat=75, change_pct=-0.8, stock_count=10),
        SectorInfo(name="消费", heat=65, change_pct=1.5, stock_count=10),
        SectorInfo(name="金融", heat=60, change_pct=2.0, stock_count=10),
    ]


@router.get("/{sector_name}/stocks", response_model=List[StockScore])
async def get_sector_stocks(sector_name: str):
    """获取指定板块 Top 10 股票列表"""
    # TODO: 实现真实数据
    return [
        StockScore(code="688008", name="澜起科技", price=65.20, change_pct=3.2, total_score=86, rating="A+"),
        StockScore(code="300782", name="卓胜微", price=112.50, change_pct=1.8, total_score=82, rating="A+"),
        StockScore(code="603986", name="兆易创新", price=98.30, change_pct=-0.5, total_score=78, rating="A"),
    ]
