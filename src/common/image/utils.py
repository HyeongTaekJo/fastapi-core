import os
from os.path import join, exists, dirname
from shutil import move
import logging

logger = logging.getLogger(__name__)

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

def restore_backups(backups: list[tuple[str, str]]):
    for original, backup in backups:
        if exists(backup):
            move(backup, original)
            logger.warning(f"⛔ 복원: {backup} → {original}")

def delete_backups(backups: list[tuple[str, str]]):
    for _, backup in backups:
        if exists(backup):
            os.remove(backup)
            logger.info(f"🗑️ 삭제됨: {backup}")

def move_temp_file_to_target(temp_path: str, target_path: str):
    os.makedirs(dirname(target_path), exist_ok=True)
    move(temp_path, target_path)
    logger.info(f"✅ 이동 완료: {temp_path} → {target_path}")
