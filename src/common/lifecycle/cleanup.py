import os
import time
from pathlib import Path
import logging
from cache.redis_connection import redis
from common.const.path_consts import TEMP_FOLDER_PATH, FILE_UPLOAD_PATH, TEMP_BACKUP_PATH
from common.file.repository import FileRepository
from database.mysql_connection import async_session_maker


logger = logging.getLogger(__name__)

async def cleanup_temp_files():
    now = time.time()
    deleted_count = 0

    for file in Path(TEMP_FOLDER_PATH).glob("*"):
        if not file.is_file():
            continue

        redis_key = f"temp_file:{file.name}"

        try:
            redis_value = await redis.get(redis_key)  # ✅ await 사용
            if redis_value:
                continue

            if now - file.stat().st_mtime > 7200:  # ✅ 2시간 넘으면 삭제
                file.unlink()
                deleted_count += 1
                logger.info(f"🧹 삭제된 temp 파일: {file.name}")

        except Exception as e:
            logger.error(f"❌ 삭제 실패: {file.name} - {e}")

    logger.info(f"✅ 이번 실행에서 삭제된 파일 수: {deleted_count}")

async def cleanup_orphan_files():
    async with async_session_maker() as session:
        repo = FileRepository(session)  # ✅ 세션을 직접 주입
        db_paths = await repo.get_all_file_paths()
        db_path_set = set(db_paths)

        deleted = 0
        for root, _, files in os.walk(FILE_UPLOAD_PATH):
            for name in files:
                rel_path = os.path.relpath(os.path.join(root, name), FILE_UPLOAD_PATH).replace("\\", "/")

                if rel_path not in db_path_set:
                    try:
                        os.remove(os.path.join(FILE_UPLOAD_PATH, rel_path))
                        logger.info(f"🧹 고아 파일 삭제됨: {rel_path}")
                        deleted += 1
                    except Exception as e:
                        logger.warning(f"⚠️ 고아 파일 삭제 실패: {rel_path} - {e}")

        logger.info(f"✅ 고아 파일 정리 완료: {deleted}개 삭제됨")

def cleanup_backups():
    now = time.time()
    deleted = 0

    for file in Path(TEMP_BACKUP_PATH).rglob("*"):
        if file.is_file() and (now - file.stat().st_mtime > 3600):  # 1시간 이상
            try:
                file.unlink()
                logger.info(f"🧹 삭제된 백업 파일: {file}")
                deleted += 1
            except Exception as e:
                logger.error(f"❌ 백업 삭제 실패: {file} - {e}")

    logger.info(f"✅ 백업 폴더 정리 완료: {deleted}개 삭제됨")
