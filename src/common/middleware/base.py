# common/middleware/base.py
import uuid
import time
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from common.utils.log_context import request_id_ctx_var, user_id_ctx_var

from auth.service import decode_jwt_token  # 직접 구현 필요
from database.mysql_connection import async_session_maker
from cache.redis_connection import redis
from database.session_context import set_db_context
from cache.redis_context import set_redis_context
from common.exceptions.base import AppException

logger = logging.getLogger(__name__)

# [1] request_id, user_id 저장
async def log_context_middleware(request: Request, call_next):
    # Nginx, Kong, Traefik 같은 API Gateway에서 X-Request-ID를 자동 생성해서 전달(추후, 변경 필요)
    try:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request_id_ctx_var.set(request_id)

        user = getattr(request.state, "user", None)
        user_id_ctx_var.set(getattr(user, "id", None) if user else None)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as e:
        logger.warning(f"[LOG_CONTEXT] 처리 실패: {e}")
        return _middleware_error_response(e)


# [2] 요청/응답 로깅
async def request_logger_middleware(request: Request, call_next):
    try:
        start = time.time()
        response = await call_next(request)  # 여기까지가 다른 미들웨어들 먼저 실행됨
        duration = round(time.time() - start, 4)

        logger.info(f"{request.method} {request.url.path} [{response.status_code}] {duration}s")
        return response
    except Exception as e:
        logger.warning(f"[REQUEST_LOGGER] 처리 실패: {e}")
        return _middleware_error_response(e)


# [3] DB 세션 주입
async def db_session_middleware(request: Request, call_next):
    try:
        async with async_session_maker() as session:
            set_db_context(session)  # ContextVar에 저장
            response = await call_next(request)
            return response
    except Exception as e:
        logger.warning(f"[DB_SESSION] 처리 실패: {e}")
        return _middleware_error_response(e)


# [4] 사용자 인증
async def auth_middleware(request: Request, call_next):
    try:
        auth_header = request.headers.get("Authorization", "")

        # Basic 토큰이면 무시하고 바로 넘김
        if auth_header.startswith("Basic "):
            return await call_next(request)

        # Bearer 토큰 처리
        token = auth_header.replace("Bearer ", "")
        user = decode_jwt_token(token) if token else None
        request.state.user = user
        user_id_ctx_var.set(user.id if user else None)

        return await call_next(request)

    except Exception as e:
        logger.warning(f"[AUTH] 인증 실패: {e}")
        return _middleware_error_response(e)


# [5] Redis 세션 주입
async def redis_middleware(request: Request, call_next):
    try:
        set_redis_context(redis)
        return await call_next(request)
    except Exception as e:
        logger.warning(f"[REDIS] 처리 실패: {e}")
        return _middleware_error_response(e)


#  공통 예외 응답 처리 함수
def _middleware_error_response(e: Exception):
    if isinstance(e, AppException):
        return JSONResponse(status_code=e.status_code, content=e.to_dict())

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "미들웨어 처리 중 서버 오류가 발생했습니다.",
                "status_code": 500,
            }
        },
    )
