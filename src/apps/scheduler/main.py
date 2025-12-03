from __future__ import annotations
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.executors.pool import ThreadPoolExecutor
from pytz import timezone

from src.core.config import settings
from src.apps.scheduler.jobs import do_initial

log = logging.getLogger(__name__)
_scheduler: BackgroundScheduler | None = None

def _register_jobs(sched: BackgroundScheduler):
    tz = timezone(settings.SCHED_TZ or "Asia/Seoul")
    max_workers = int(settings.SCHED_MAX_WORKERS or 8)

    test_iv = int(settings.SCHED_TEST_INTERVAL_DAY or 0)

    for slug, cron in [("KP", settings.CRON_KAKAOPAGE), ("NS", settings.CRON_NAVERSERIES)]:
        if test_iv > 0:
            trig = IntervalTrigger(days=test_iv, timezone=tz)
            jname = f"initial_full-{slug}-interval"
        else:
            trig = CronTrigger.from_crontab(cron, timezone=tz)
            jname = f"initial_full-{slug}"

        sched.add_job(
            func=do_initial,
            trigger=trig,
            id=jname,
            name=jname,
            kwargs={"platform_slug": slug, "max_workers": max_workers},
            replace_existing=True,
            max_instances=1,        # 같은 잡 동시 실행 방지(프로세스 내부)
        )
        log.info("Scheduled %s", jname)

def start_scheduler() -> BackgroundScheduler | None:
    global _scheduler
    if _scheduler:
        return _scheduler

    executors = {
        'default': ThreadPoolExecutor(max_workers=1),  # 동시에 1개만 실행
    }
    sched = BackgroundScheduler(executors=executors,timezone=settings.TZ)
    _register_jobs(sched)
    try:
        sched.start()
        log.info("Scheduler started.")
    except (KeyboardInterrupt, SystemExit):
        log.info("Scheduler stopped.")
    _scheduler = sched
    return sched

def shutdown_scheduler():
    global _scheduler
    if _scheduler:
        try:
            _scheduler.shutdown(wait=False)
            log.info("Scheduler stopped.")
        finally:
            _scheduler = None
