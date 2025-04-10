from apscheduler.schedulers.asyncio import AsyncIOScheduler
from common.lifecycle.cleanup import cleanup_temp_files, cleanup_backups, cleanup_orphan_files

scheduler = AsyncIOScheduler()

def start_scheduler():
    scheduler.add_job(cleanup_temp_files, "interval", minutes=30)
    scheduler.add_job(cleanup_backups, "interval", hours=1)
    scheduler.add_job(cleanup_orphan_files, "cron", hour="3")  # 매일 새벽 3시
    scheduler.start()
