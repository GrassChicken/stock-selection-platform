"""定时任务调度器 — M6 接入真实引擎 + 飞书通知"""
import threading
from datetime import datetime
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


def is_trading_day() -> bool:
    """判断是否为交易日（跳过法定节假日）
    
    简化版：周一至周五即认为是交易日，
    如需精确排除法定节假日，可接入交易所日历 API。
    """
    now = datetime.now()
    # 0=周一, 6=周日
    return now.weekday() < 5


def run_daily_analysis():
    """每日定时分析任务（后台线程执行，不阻塞 scheduler）"""
    if not is_trading_day():
        print(f"⏰ 非交易日，跳过定时分析 ({datetime.now().strftime('%Y-%m-%d')})")
        return

    print(f"⏰ 开始每日定时分析... ({datetime.now().strftime('%Y-%m-%d %H:%M')})")

    def _run():
        try:
            from app.engine.pipeline import run_full_analysis
            t0 = datetime.now()
            result = run_full_analysis(sample_size=500)
            elapsed = (datetime.now() - t0).total_seconds()

            # 存储到 analyze 模块缓存
            try:
                from app.api import analyze
                analyze._latest_result = result
            except ImportError:
                pass

            print(f"✅ 每日定时分析完成 (耗时{elapsed:.0f}s)")

            # 飞书通知
            stats = result.get('stats', {})
            sectors = result.get('sectors', [])
            msg = (
                f"🦐 智能选股日报 ({datetime.now().strftime('%m-%d')})\n"
                f"总股票: {stats.get('total', 0)}只 | 通过: {stats.get('passed', 0)}只 | 排除: {stats.get('rejected', 0)}只\n"
                f"A+优质: {stats.get('A+', 0)} | A良好: {stats.get('A', 0)} | B一般: {stats.get('B', 0)} | C较弱: {stats.get('C', 0)}\n"
            )
            if sectors:
                msg += "\n🔥 热门板块:\n"
                for s in sectors[:3]:
                    msg += f"  {s['name']} (热度{s['heat']}, {s['stock_count']}只)\n"
            msg += f"\n耗时: {result.get('elapsed', 0):.0f}s"
            send_feishu_notify(msg)

        except Exception as e:
            print(f"❌ 定时分析失败: {e}")
            send_feishu_notify(f"❌ 选股分析失败: {e}")

    threading.Thread(target=_run, daemon=True).start()


def send_feishu_notify(text: str):
    """发送飞书通知（webhook）"""
    import json
    import urllib.request
    try:
        settings = get_settings()
        webhook_url = getattr(settings, 'FEISHU_WEBHOOK', '')
        if not webhook_url:
            print(f"📢 飞书通知 (未配置webhook):\n{text}")
            return

        payload = json.dumps({
            "msg_type": "text",
            "content": {"text": text}
        }).encode('utf-8')
        req = urllib.request.Request(
            webhook_url, data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"📢 飞书通知已发送: {resp.status}")
    except Exception as e:
        print(f"⚠️ 飞书通知失败: {e}")
