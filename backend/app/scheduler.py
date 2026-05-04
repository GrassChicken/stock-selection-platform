"""定时任务调度器"""
from apscheduler.schedulers.background import BackgroundScheduler
from app.models import ScheduleConfig
from app.config import get_settings

_scheduler = BackgroundScheduler()
_schedule_config = ScheduleConfig()


def init_scheduler():
    """初始化调度器"""
    settings = get_settings()
    global _schedule_config
    _schedule_config = ScheduleConfig(
        enabled=settings.SCHEDULE_ENABLED,
        hour=settings.SCHEDULE_HOUR,
        minute=settings.SCHEDULE_MINUTE,
    )

    if _schedule_config.enabled:
        _scheduler.add_job(
            run_daily_analysis,
            "cron",
            hour=_schedule_config.hour,
            minute=_schedule_config.minute,
            day_of_week="mon-fri",
            id="daily_analysis",
            replace_existing=True,
        )
        print(f"⏰ 定时分析已启用: 每周一至周五 {_schedule_config.hour:02d}:{_schedule_config.minute:02d}")

    if not _scheduler.running:
        _scheduler.start()


def shutdown_scheduler():
    """关闭调度器"""
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        print("⏰ 定时分析已关闭")


def get_schedule_config() -> ScheduleConfig:
    return _schedule_config


def update_schedule_config(cfg: ScheduleConfig) -> ScheduleConfig:
    global _schedule_config
    _schedule_config = cfg

    if _scheduler.get_job("daily_analysis"):
        _scheduler.remove_job("daily_analysis")

    if cfg.enabled:
        _scheduler.add_job(
            run_daily_analysis,
            "cron",
            hour=cfg.hour,
            minute=cfg.minute,
            day_of_week="mon-fri",
            id="daily_analysis",
            replace_existing=True,
        )

    return _schedule_config


def run_daily_analysis():
    """每日定时分析任务"""
    print("⏰ 开始每日定时分析...")
    # TODO: 调用 L1 -> L2 -> 板块分组 引擎
    print("✅ 每日定时分析完成")
