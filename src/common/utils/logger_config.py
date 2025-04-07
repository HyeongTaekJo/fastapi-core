import os
import logging
from logging.config import dictConfig
from dotenv import load_dotenv
from pathlib import Path
from common.utils.log_context import request_id_ctx_var, user_id_ctx_var

load_dotenv()

level = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVEL = getattr(logging, level, logging.INFO)

# ✅ logs 폴더를 프로젝트 루트 기준으로 만들기
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # ex) src/common/utils/logger_config.py → Backend/
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)  # logs 폴더 없으면 생성
LOG_FILE_PATH = LOGS_DIR / "app.log"

# ✅ 요청 단위 request_id, user_id 추적용 필터 클래스
class RequestContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx_var.get(None)
        record.user_id = user_id_ctx_var.get(None)
        return True

def setup_logging():
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s] [req_id:%(request_id)s user:%(user_id)s] %(filename)s:%(lineno)d - %(message)s"
            },
        },
        "filters": {
            "request_context": {
                '()': RequestContextFilter
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": LOG_LEVEL,
                "formatter": "default",
                "filters": ["request_context"],
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "level": LOG_LEVEL,
                "formatter": "default",
                "filters": ["request_context"],
                "filename": str(LOG_FILE_PATH),
                "when": "midnight",
                "interval": 1,
                "backupCount": 7,
                "encoding": "utf-8",
            },
        },
        "root": {
            "level": LOG_LEVEL,
            "handlers": ["console", "file"],
        },
    }

    dictConfig(log_config)