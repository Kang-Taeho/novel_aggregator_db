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
log.propagate = True
log.setLevel(logging.INFO)

_scheduler: BackgroundScheduler | None = None

def _register_jobs(sched: BackgroundScheduler):
    """
    APScheduler에 실제 잡을 등록한다.

    - 운영 환경: Cron 기반 반복 실행
    - 테스트 환경: Interval 기반 반복 실행
    - 플랫폼별(KP / NS) worker 수 다르게 적용
    - 동일 작업 중복 실행 방지 / misfire / coalesce 정책 설정
    """
    tz = timezone(settings.TZ or "Asia/Seoul")
    # 테스트 모드 여부 판단
    # - 시간 단위 interval 또는 초 단위 interval 이 설정된 경우
    test_iv = (int(settings.SCHED_TEST_INTERVAL_HOURS) or
               int(settings.SCHED_TEST_INTERVAL_SECONDS) or 0)

    for slug, cron in [("KP", settings.CRON_KAKAOPAGE), ("NS", settings.CRON_NAVERSERIES)]:
        # ---------------- 테스트 모드 ----------------
        if test_iv > 0:
            if int(settings.SCHED_TEST_INTERVAL_SECONDS) > 0 :
                trig = IntervalTrigger(seconds=test_iv, timezone=tz)
                jname = f"initial_full-{slug}-interval_seconds"
            else :
                trig = IntervalTrigger(hours=test_iv, timezone=tz)
                jname = f"initial_full-{slug}-interval_hours"
            test_bool = True
        # ---------------- 운영 모드 (크론 스케줄) ----------------
        else:
            trig = CronTrigger.from_crontab(cron, timezone=tz)
            jname = f"initial_full-{slug}"
            test_bool = False

        # ---------------- 플랫폼별 worker 설정 ----------------
        if slug == "KP": max_workers = int(settings.SCHED_MAX_WORKERS_KP)
        elif slug == "NS": max_workers = int(settings.SCHED_MAX_WORKERS_NS)
        else: max_workers = 8

        # ---------------- Job 등록 ----------------
        sched.add_job(
            func=do_initial,
            trigger=trig,
            id=jname,
            name=jname,
            kwargs={"platform_slug": slug, "max_workers": max_workers, "test_bool":test_bool},
            replace_existing=True,               # 기존 동일 job 교체
            max_instances=1,                     # 동일 job 중복 실행 방지
            misfire_grace_time=3600,             # 1시간 이내 늦게라도 실행 허용
            coalesce=True                        # 밀린 스케줄은 1회로 병합
        )
        log.info("Scheduled %s", jname)

def start_scheduler() -> BackgroundScheduler | None:
    """
    백그라운드 APScheduler 시작.

    - 이미 실행 중이면 기존 인스턴스 반환
    - ThreadPoolExecutor(1) → 동시에 1개 job만 실행 보장
    """
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
    """
    APScheduler 안전 종료
    """
    global _scheduler
    if _scheduler:
        try:
            _scheduler.shutdown(wait=False)
        finally:
            _scheduler = None
