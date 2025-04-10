import os
from fastapi import HTTPException
from common.file.repository import FileRepository
from common.file.enums.owner_type_enum import OWNER_TYPE_MAPPING
from common.file.file_utils import (
    get_file_type_by_ext,
    backup_files,
    restore_backups,
    delete_backups,
    move_temp_file_to_target
)
from common.const.path_consts import TEMP_FOLDER_PATH, TEMP_BACKUP_PATH
import logging

logger = logging.getLogger(__name__)


class FileService:
    def __init__(self, target_folder_path: str):
        self.repo = FileRepository()
        self.target_folder_path = target_folder_path

    async def save_files(self, owner_type: str, owner_id: int, temp_filenames: list[str]):
        await self.prepare_for_save_or_update(owner_type, owner_id)

        try:
            for index, filename in enumerate(temp_filenames):
                temp_path = os.path.join(TEMP_FOLDER_PATH, filename)
                target_rel_path = os.path.join(owner_type, filename)
                target_path = os.path.join(self.target_folder_path, target_rel_path)

                await self.move_from_temp_and_link(
                    temp_filename=filename,
                    owner_type=owner_type,
                    owner_id=owner_id,
                    is_main=(index == 0),
                    description=None,
                    order=index
                )

                self.record_moved_file(temp_path, target_path)

            await self.finalize_delete_old_records(owner_type, owner_id)

        except Exception as e:
            await self.rollback()
            raise e

    async def move_from_temp_and_link(
        self,
        temp_filename: str,
        owner_type: str,
        owner_id: int,
        description: str | None = None,
        is_main: bool = False,
        order: int = 0
    ):
        # ✅ 모델별 하위 폴더 생성: post/uuid.jpg, user/uuid.pdf 등
        subfolder = owner_type
        target_rel_path = os.path.join(subfolder, temp_filename)
        temp_path = os.path.join(TEMP_FOLDER_PATH, temp_filename)
        target_path = os.path.join(self.target_folder_path, target_rel_path)

        backups = []

        try:
            # # ✅ 기존 연결된 파일 백업 및 DB 삭제
            # existing_files = await self.repo.get_files_by_owner(owner_type, owner_id)
            # old_paths = [f.path for f in existing_files]

            # if old_paths:
            #     backups = backup_files(old_paths, self.target_folder_path, TEMP_BACKUP_PATH)
            #     await self.repo.delete_files_by_owner(owner_type, owner_id)

            if not os.path.exists(temp_path):
                raise FileNotFoundError("임시 파일이 존재하지 않습니다.")

            move_temp_file_to_target(temp_path, target_path)

            file_type = get_file_type_by_ext(temp_filename)
            size = os.path.getsize(target_path)

            mapping_field = OWNER_TYPE_MAPPING.get(owner_type)
            if not mapping_field:
                raise ValueError(f"Invalid owner type: {owner_type}")

            file_record = await self.repo.create_file_record(
                path=target_rel_path,  # 상대 경로 저장: post/uuid.png
                original_name=temp_filename,
                size=size,
                type=file_type,
                is_main=is_main,
                description=description,
                owner_type=owner_type,
                owner_id=owner_id,
                order=order,
                **{mapping_field: owner_id}
            )

            delete_backups(backups)

            return file_record

        except Exception as e:
            # ✅ 실패 시 롤백: 새로 옮긴 파일 복귀 + 백업 복원
            if os.path.exists(target_path):
                move_temp_file_to_target(target_path, temp_path)
                logger.warning(f"⛔ 파일 롤백됨: {target_path} → {temp_path}")

            restore_backups(backups)

            logger.error(f"❌ 파일 처리 중 오류 발생: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "FILE_SAVE_FAILED",
                    "message": "파일 저장 중 오류 발생. 롤백되었습니다.",
                    "reason": str(e),
                }
            )
        
    async def prepare_for_save_or_update(self, owner_type: str, owner_id: int):
        """
        기존 파일을 백업만 수행 (DB 삭제는 나중에 성공 후)
        """
        existing_files = await self.repo.get_files_by_owner(owner_type, owner_id)
        old_paths = [f.path for f in existing_files]

        self._backups = backup_files(old_paths, self.target_folder_path, TEMP_BACKUP_PATH)
        self._old_files = existing_files  # 삭제는 save 끝나고 수행

    async def delete_by_owner(self, owner_type: str, owner_id: int):
        files = await self.repo.get_files_by_owner(owner_type, owner_id)

        for file in files:
            full_path = os.path.join(self.target_folder_path, file.path)
            if os.path.exists(full_path):
                os.remove(full_path)

        await self.repo.delete_files_by_owner(owner_type, owner_id)

    async def get_files_by_owner(self, owner_type: str, owner_id: int):
        return await self.repo.get_files_by_owner(owner_type, owner_id)
    
    def record_moved_file(self, src: str, dest: str):
        if not hasattr(self, "_moved_files"):
            self._moved_files = []
        self._moved_files.append((src, dest))

    async def rollback(self):
        if hasattr(self, "_moved_files"):
            for temp_path, target_path in reversed(self._moved_files):
                if os.path.exists(target_path):
                    move_temp_file_to_target(target_path, temp_path)
                    logger.warning(f"⛔ 파일 롤백됨: {target_path} → {temp_path}")

        if hasattr(self, "_backups"):
            restore_backups(self._backups)
            logger.warning("⛔ 백업된 파일 복원 완료")

    async def finalize_delete_old_records(self, owner_type: str, owner_id: int):
        """
        모든 파일 저장 성공 후 → 기존 DB 파일 레코드 삭제
        """
        await self.repo.delete_files_by_owner(owner_type, owner_id)
        delete_backups(self._backups)