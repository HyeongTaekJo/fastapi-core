import logging
from pathlib import Path
from fastapi import FastAPI
from common.lifecycle.lifespan import lifespan
from fastapi.staticfiles import StaticFiles
from common.const.settings import settings
from common.const.path_consts import PUBLIC_FOLDER_PATH
from common.middleware.base import (
    log_context_middleware,
    request_logger_middleware,
    db_session_middleware,
    auth_middleware,
    redis_middleware
)

# 로깅 설정 적용 (.env 기반 + TimedRotatingFileHandler)
from common.utils.logger_config import setup_logging
setup_logging()


# 예외 핸들러 import
from common.exceptions.handlers import (
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from common.exceptions.base import AppException
from fastapi.middleware.cors import CORSMiddleware

# 라우터 import
from post.route import router as post_router
from user.route import router as user_router
from auth.route import router as auth_router
from common.image.router import router as common_image_router
from common.file.router import router as common_file_router

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True, # 쿠키 허용
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# 사용자 정의 미들웨어
app.middleware("http")(request_logger_middleware)  # 가장 바깥
app.middleware("http")(log_context_middleware)     # 로그 ID 설정
app.middleware("http")(db_session_middleware)      # DB 세션 설정
app.middleware("http")(redis_middleware)           # Redis 인스턴스 설정
app.middleware("http")(auth_middleware)            # 토큰 검증

# 예외 핸들러 등록
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)
# 필요하면 로깅 설정 Sentry 연동, Slack 알림 등도 연결 가능

# 정적 파일 마운트
app.mount("/public", StaticFiles(directory=PUBLIC_FOLDER_PATH), name="public")

# 라우터 등록
app.include_router(post_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(common_image_router)
app.include_router(common_file_router)

# 헬스체크
@app.get("/")
async def health():
    return {"status": "connect success"}
