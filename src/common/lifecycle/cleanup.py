import os
import time
from pathlib import Path
import logging
from cache.redis_connection import redis
from common.const.path_consts import TEMP_FOLDER_PATH, FILE_UPLOAD_PATH, TEMP_BACKUP_PATH
from common.file.repository import FileRepository


logger = logging.getLogger(__name__)

def cleanup_temp_files():
    now = time.time()
    deleted_count = 0

    for file in Path(TEMP_FOLDER_PATH).glob("*"):
        if not file.is_file():
            continue

        redis_key = f"temp_file:{file.name}"  # ✅ 범용 키

        try:
            # Redis TTL이 남아있으면 삭제 건너뜀
            if redis.get(redis_key):
                continue

            # 2시간 이상 지난 경우만 삭제
            if now - file.stat().st_mtime > 7200:
                file.unlink()
                deleted_count += 1
                logger.info(f"🧹 삭제된 temp 파일: {file.name}")

        except Exception as e:
            logger.error(f"❌ 삭제 실패: {file.name} - {e}")

    logger.info(f"✅ 이번 실행에서 삭제된 파일 수: {deleted_count}")

async def cleanup_orphan_files():
    repo = FileRepository()
    db_paths = await repo.get_all_file_paths()  # 상대 경로 리스트 반환
    db_path_set = set(db_paths)

    deleted = 0
    for root, _, files in os.walk(FILE_UPLOAD_PATH):
        for name in files:
            rel_path = os.path.relpath(os.path.join(root, name), FILE_UPLOAD_PATH)
            rel_path = rel_path.replace("\\", "/")

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
        if file.is_file() and (now - file.stat().st_mtime > 60 * 60):  # 1시간 이상
            try:
                file.unlink()
                logger.info(f"🧹 삭제된 백업 파일: {file}")
                deleted += 1
            except Exception as e:
                logger.error(f"❌ 백업 삭제 실패: {file} - {e}")

    logger.info(f"✅ 백업 폴더 정리 완료: {deleted}개 삭제됨")
