from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.mysql_connection import async_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # FastAPI 인스턴스 기동시 필요한 작업 수행. 
    print("Starting up...")
    yield

    #FastAPI 인스턴스 종료시 필요한 작업 수행
    print("Shutting down...")
    await async_engine.dispose()


# 추후 고도화@asynccontextmanager
# async def lifespan(app: FastAPI):
#     logger.info("🚀 Starting up...")

#     # ✅ 예: DB, Redis 연결 테스트
#     try:
#         await test_db_connection()
#         await test_redis_connection()
#         logger.info("✅ Connected to DB and Redis.")
#     except Exception as e:
#         logger.critical(f"❌ Startup failed: {e}")
#         raise e

#     # ✅ 예: 모니터링 연동 (Prometheus, Sentry 등)
#     init_prometheus(app)
#     init_sentry()

#     yield

#     logger.info("📴 Shutting down...")

#     # ✅ 연결 종료
#     await async_engine.dispose()
#     await close_redis()

#     # ✅ 기타 정리 (예: 작업큐 종료, 임시파일 정리)
#     await graceful_shutdown_tasks()
#     logger.info("✅ Cleanup done. Bye 👋")

