import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from auth.service import decode_jwt_token
from common.utils.log_context import user_id_ctx_var
from common.middleware.error import middleware_error_handler

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """사용자 인증을 처리하는 미들웨어"""
        try:
            auth_header = request.headers.get("Authorization", "")

            # Basic 토큰이면 무시하고 바로 넘김
            if auth_header.startswith("Basic "):
                return await call_next(request)

            # Bearer 토큰 처리
            token = auth_header.replace("Bearer ", "")
            user = decode_jwt_token(token) if token else None

            user_id_ctx_var.set(user.id if user else None)

            return await call_next(request)

        except Exception as e:
            logger.warning(f"[AUTH] 인증 실패: {e}")
            return middleware_error_handler(e) 