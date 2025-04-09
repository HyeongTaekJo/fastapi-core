from apscheduler.schedulers.asyncio import AsyncIOScheduler
from common.lifecycle.temp_cleanup import cleanup_temp_images

scheduler = AsyncIOScheduler()

def start_scheduler():
    scheduler.add_job(cleanup_temp_images, "interval", seconds=1800)
    scheduler.start()