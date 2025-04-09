import os
import time
from pathlib import Path
import logging
from cache.redis_connection import redis
from common.const.path_consts import TEMP_FOLDER_PATH

logger = logging.getLogger(__name__)

def cleanup_temp_images():
    now = time.time()
    deleted_count = 0

    for file in Path(TEMP_FOLDER_PATH).glob("*"):
        if not file.is_file():
            continue

        # Redis에 TTL 키가 있으면 삭제하지 않음
        redis_key = f"temp_img:{file.name}"

        try:
            # Redis에 아직 살아 있으면 삭제 건너뜀
            if redis.get(redis_key):
                continue

            # 2시간 이상 지난 경우만 삭제
            if now - file.stat().st_mtime > 7200:
                file.unlink()
                deleted_count += 1
                logger.info(f"🧹 삭제된 temp 파일: {file.name}")

        except Exception as e:
            logger.error(f"❌ 삭제 실패: {file.name} - {e}")

    logger.info(f"✅ 이번 실행에서 삭제된 이미지 수: {deleted_count}")
