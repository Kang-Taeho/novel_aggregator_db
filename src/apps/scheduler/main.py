from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz
from src.core.config import settings
from src.pipeline.orchestrator import run_initial_full as run_pipeline_daily

tz = pytz.timezone(settings.TZ)
def job(platform_slug: str):
    def _inner():
        print(f"[{datetime.now(tz).isoformat()}] job: {platform_slug}")
        run_pipeline_daily(platform_slug=platform_slug)
    return _inner

def main():
    sched = BlockingScheduler(timezone=tz)
    for slug, cron in [("KP", settings.CRON_KAKAOPAGE), ("NS", settings.CRON_NAVERSERIES), ("MP", settings.CRON_MUNPIA)]:
        sched.add_job(job(slug), CronTrigger.from_crontab(cron, timezone=tz), id=slug)
    print("Scheduler started. Ctrl+C to stop.")
    try: sched.start()
    except (KeyboardInterrupt, SystemExit): print("Scheduler stopped.")

if __name__ == "__main__": main()
