import os
from shutil import move
from os.path import join, exists, dirname
from pathlib import Path
import logging
from common.file.file_enum import FileModelType

logger = logging.getLogger(__name__)

# ✅ 1. 확장자 기준 파일 타입 추정
ALLOWED_FILE_TYPES = {
    FileModelType.IMAGE: {".jpg", ".jpeg", ".png"},
    FileModelType.PDF: {".pdf"},
    FileModelType.EXCEL: {".xls", ".xlsx"},
    FileModelType.PPT: {".ppt", ".pptx"},
    FileModelType.WORD: {".doc", ".docx"},
    FileModelType.HWP: {".hwp"},
    FileModelType.OTHER: set(),
}

def get_file_type_by_ext(filename: str) -> FileModelType:
    ext = Path(filename).suffix.lower()
    for file_type, extensions in ALLOWED_FILE_TYPES.items():
        if ext in extensions:
            return file_type
    return FileModelType.OTHER

# ✅ 2. 업로드 가능한 파일 검증
MAX_UPLOAD_FILE_SIZE_MB = 10

def validate_file(file) -> None:
    file_type = get_file_type_by_ext(file.filename)
    if file_type == FileModelType.OTHER:
        raise ValueError("지원하지 않는 파일 형식입니다.")

    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_UPLOAD_FILE_SIZE_MB * 1024 * 1024:
        raise ValueError("파일 크기가 너무 큽니다.")

# ✅ 3. 파일 백업: 원본 → 백업 디렉토리
def backup_files(paths: list[str], src_root: str, backup_root: str) -> list[tuple[str, str]]:
    backups = []
    for rel_path in paths:
        original = join(src_root, rel_path)
        backup = join(backup_root, rel_path)
        if exists(original):
            os.makedirs(dirname(backup), exist_ok=True)
            move(original, backup)
            backups.append((original, backup))
            logger.info(f"🔄 백업: {original} → {backup}")
    return backups

# ✅ 4. 복원: 백업 → 원래 위치
def restore_backups(backups: list[tuple[str, str]]):
    for original, backup in backups:
        if exists(backup):
            move(backup, original)
            logger.warning(f"⛔ 복원: {backup} → {original}")

# ✅ 5. 백업 삭제
def delete_backups(backups: list[tuple[str, str]]):
    for _, backup in backups:
        if exists(backup):
            os.remove(backup)
            logger.info(f"🗑️ 삭제됨: {backup}")

# ✅ 6. temp → 최종 디렉토리 이동
def move_temp_file_to_target(temp_path: str, target_path: str):
    os.makedirs(dirname(target_path), exist_ok=True)
    move(temp_path, target_path)
    logger.info(f"✅ 이동 완료: {temp_path} → {target_path}")
