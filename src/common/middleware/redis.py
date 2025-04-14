import logging
from fastapi import Request
from cache.redis_connection import redis
from cache.redis_context import set_redis_context
from common.middleware.error import middleware_error_handler

logger = logging.getLogger(__name__)

async def redis_middleware(request: Request, call_next):
    """Redis 인스턴스를 컨텍스트에 주입하는 미들웨어"""
    try:
        set_redis_context(redis)
        return await call_next(request)
    except Exception as e:
        logger.warning(f"[REDIS] 처리 실패: {e}")
        return middleware_error_handler(e) 