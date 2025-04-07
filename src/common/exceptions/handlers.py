from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from .base import AppException
import logging

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# 커스텀 AppException 처리 핸들러
# ------------------------------------------------------------------------------

async def app_exception_handler(request: Request, exc: AppException):
    logger.warning(f"Handled AppException: {exc.code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )

# ✅ 사용 예시:
# from common.exceptions.base import UnauthorizedException
# raise UnauthorizedException("로그인이 필요합니다.")

# 또는
# raise NotFoundException("Post")
# raise ConflictException("이미 등록된 이메일입니다.")


# ------------------------------------------------------------------------------
# 입력값 검증 실패 (Pydantic ValidationError)
# ------------------------------------------------------------------------------

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation failed: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "status_code": 422,
                "details": exc.errors()
            }
        }
    )

# ✅ 사용 예시:
# class LoginSchema(BaseModel):
#     email: str
#     password: str
#
# @router.post("/login")
# async def login(req: LoginSchema): ...
#
# → email이나 password가 누락되거나 타입이 다르면 자동으로 이 핸들러가 호출됨


# ------------------------------------------------------------------------------
# FastAPI 기본 HTTPException
# ------------------------------------------------------------------------------

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(
        f"Unhandled HTTPException: {exc.status_code} - {exc.detail} | {request.method} {request.url.path}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "status_code": exc.status_code
            }
        }
    )

# ✅ 사용 예시:
# from fastapi import HTTPException, status
# raise HTTPException(status_code=403, detail="접근이 금지되었습니다.")
# raise HTTPException(status_code=404, detail="페이지를 찾을 수 없습니다.")


# ------------------------------------------------------------------------------
# 예기치 못한 서버 내부 오류
# ------------------------------------------------------------------------------

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unexpected server error: {exc} | {request.method} {request.url.path}", 
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "서버 내부 오류가 발생했습니다.",
                "status_code": 500
            }
        }
    )

# ✅ 사용 예시:
# 그냥 일반적인 에러가 발생했을 때 (예: 1 / 0, attribute 접근 실패 등)
# FastAPI가 이 핸들러로 자동 전송
