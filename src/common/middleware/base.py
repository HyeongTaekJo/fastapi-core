# common/middleware/base.py
import uuid
import time
import logging
from fastapi import Request
from common.utils.log_context import request_id_ctx_var, user_id_ctx_var

from auth.service import decode_jwt_token  # 직접 구현 필요
from database.mysql_connection import async_session_maker
from cache.redis_connection import redis
from database.session_context import set_db_context
from cache.redis_context import set_redis_context

logger = logging.getLogger(__name__)

# [1] request_id, user_id 저장
async def log_context_middleware(request: Request, call_next):
    # Nginx, Kong, Traefik 같은 API Gateway에서 X-Request-ID를 자동 생성해서 전달(추후, 변경 필요)
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request_id_ctx_var.set(request_id)

    user = getattr(request.state, "user", None)
    user_id_ctx_var.set(getattr(user, "id", None) if user else None)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# [2] 요청/응답 로깅
async def request_logger_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request) #  여기까지가 다른 미들웨어들 먼저 실행됨
    duration = round(time.time() - start, 4)

    logger.info(f"{request.method} {request.url.path} [{response.status_code}] {duration}s")
    return response

# [3] DB 세션 주입
async def db_session_middleware(request, call_next):
    async with async_session_maker() as session:
        set_db_context(session)  #  ContextVar에 저장
        response = await call_next(request)
        return response

# [4] 사용자 인증
async def auth_middleware(request: Request, call_next):
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

# [5] Redis 세션 주입
async def redis_middleware(request: Request, call_next):
    set_redis_context(redis)
    return await call_next(request)