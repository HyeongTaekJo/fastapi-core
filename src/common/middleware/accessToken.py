from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from starlette.responses import JSONResponse
from auth.tokens.access_token import access_token
from starlette.status import HTTP_401_UNAUTHORIZED

class AccessTokenEnforcerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        endpoint = request.scope.get("endpoint")

        # ✅ 마킹된 엔드포인트는 통과
        if endpoint and getattr(endpoint, "_is_public", False):
            return await call_next(request)

        try:
            await access_token(request=request)
            if request.state.token_type != "access":
                raise Exception("Access Token이 아닙니다.")
        except Exception:
            return JSONResponse(
                status_code=HTTP_401_UNAUTHORIZED,
                content={"detail": "Access Token이 필요합니다."}
            )

        return await call_next(request)
