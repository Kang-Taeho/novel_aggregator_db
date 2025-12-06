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
    tz = timezone(settings.TZ or "Asia/Seoul")
    max_workers = int(settings.SCHED_MAX_WORKERS or 8)

    test_iv = (int(settings.SCHED_TEST_INTERVAL_HOURS) or
               int(settings.SCHED_TEST_INTERVAL_SECONDS) or 0)

    for slug, cron in [("KP", settings.CRON_KAKAOPAGE), ("NS", settings.CRON_NAVERSERIES)]:
        #테스트
        if test_iv > 0:
            if int(settings.SCHED_TEST_INTERVAL_SECONDS) > 0 :
                trig = IntervalTrigger(seconds=test_iv, timezone=tz)
                jname = f"initial_full-{slug}-interval_seconds"
            else :
                trig = IntervalTrigger(hours=test_iv, timezone=tz)
                jname = f"initial_full-{slug}-interval_hours"
            test_bool = True
        #실제 운영환경
        else:
            trig = CronTrigger.from_crontab(cron, timezone=tz)
            jname = f"initial_full-{slug}"
            test_bool = False

        sched.add_job(
            func=do_initial,
            trigger=trig,
            id=jname,
            name=jname,
            kwargs={"platform_slug": slug, "max_workers": max_workers, "test_bool":test_bool},
            replace_existing=True,
            max_instances=1,        # 같은 잡 동시 실행 방지(프로세스 내부)
            misfire_grace_time=3600,  # ← 지연 시 1시간 안엔 수행
            coalesce=True  # ← 밀린 실행 병합
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
    sched.start()
    _scheduler = sched
    return sched

def shutdown_scheduler():
    global _scheduler
    if _scheduler:
        try:
            _scheduler.shutdown(wait=False)
        finally:
            _scheduler = None
