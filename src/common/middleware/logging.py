import uuid
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from common.utils.log_context import request_id_ctx_var, user_id_ctx_var
from common.middleware.error import middleware_error_handler

logger = logging.getLogger(__name__)

class LogContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """Request ID와 User ID를 컨텍스트에 저장하는 미들웨어"""
        try:
            request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
            request_id_ctx_var.set(request_id)

            response = await call_next(request)

            # user = request.state.user
            # user_id_ctx_var.set(user.id if user else None)

            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as e:
            logger.warning(f"[LOG_CONTEXT] 처리 실패: {e}")
            return middleware_error_handler(e)

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """요청/응답 로깅을 처리하는 미들웨어"""
        try:
            start = time.time()
            response = await call_next(request)
            duration = round(time.time() - start, 4)

            user = getattr(request.state, "user", None)
            user_id_ctx_var.set(user.id if user else None)

            logger.info(f"{request.method} {request.url.path} [{response.status_code}] {duration}s")
            return response
        except Exception as e:
            logger.warning(f"[REQUEST_LOGGER] 처리 실패: {e}")
            return middleware_error_handler(e) 