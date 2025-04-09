from common.lifecycle.scheduler_runner import scheduler 
import logging

logger = logging.getLogger(__name__)

async def graceful_shutdown_tasks():
    logger.info("🧹 Performing graceful shutdown tasks")

    try:
        scheduler.shutdown(wait=False)  # 스케줄러 정지
        logger.info("🛑 APScheduler stopped")
    except Exception as e:
        logger.warning(f"APScheduler 종료 중 오류 발생: {e}")

    # TODO: 여기에 실제 종료 전 정리할 작업 추가
    # 예: 
    # - 백그라운드 작업 큐 종료 (예: Celery Worker / TaskQueue 중단)
    # - 외부 API 세션 닫기
    # - 파일 쓰기 정리
    # - 로그 전송 대기
    # - WebSocket 닫기 등

    # 예: 백그라운드 작업 취소
    # if background_task:
    #     background_task.cancel()

    # 예: Redis에 저장된 임시 세션 키 삭제
    # await redis.delete("some:session:key")

    # 예: 외부 API 세션 닫기
    # await external_api_session.close()

    logger.info("🧼 Graceful shutdown completed")
