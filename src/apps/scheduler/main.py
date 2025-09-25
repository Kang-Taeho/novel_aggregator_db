from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz
from src.core.config import settings
from src.data.database import SessionLocal
from src.pipeline.orchestrator import run_daily_platform as run_pipeline_daily

tz = pytz.timezone(settings.TZ)
def job(platform: str):
    def _inner():
        print(f"[{datetime.now(tz).isoformat()}] job: {platform}")
        with SessionLocal() as s:
            run_pipeline_daily(s, platform=platform)
    return _inner

def main():
    sched = BlockingScheduler(timezone=tz)
    for slug, cron in [("KP", settings.CRON_KAKAOPAGE), ("NS", settings.CRON_NAVERSERIES), ("MP", settings.CRON_MUNPIA)]:
        sched.add_job(job(slug), CronTrigger.from_crontab(cron, timezone=tz), id=slug)
    print("Scheduler started. Ctrl+C to stop.")
    try: sched.start()
    except (KeyboardInterrupt, SystemExit): print("Scheduler stopped.")

if __name__ == "__main__": main()
