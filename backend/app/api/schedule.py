"""定时任务管理 API"""
from fastapi import APIRouter
from app.models import ScheduleConfig
from app.scheduler import get_schedule_config, update_schedule_config

router = APIRouter()


@router.get("", response_model=ScheduleConfig)
async def get_schedule():
    """查看定时分析配置"""
    return get_schedule_config()


@router.put("", response_model=ScheduleConfig)
async def set_schedule(cfg: ScheduleConfig):
    """修改定时分析配置"""
    return update_schedule_config(cfg)
