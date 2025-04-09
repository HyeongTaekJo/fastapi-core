from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from database.mysql_connection import async_engine
from cache.redis_connection import redis
from common.lifecycle.startup_check import test_db_connection, test_redis_connection
from common.lifecycle.graceful_shutdown import graceful_shutdown_tasks  # 필요 시
from common.lifecycle.scheduler_runner import start_scheduler 

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting up...")

    try:
        await test_db_connection()
        await test_redis_connection()

        start_scheduler()  
        logger.info("🔗 All services connected.")
    except Exception as e:
        logger.critical("❌ Startup failed due to service connection error")
        raise e

    yield  # 앱 실행 중...

    logger.info("📴 Shutting down...")
    await async_engine.dispose()
    await redis.close()
    await graceful_shutdown_tasks() # 추후, 필요시 실제 종료 전 정리할 작업 추가
    logger.info("✅ Cleanup done. Bye 👋")



