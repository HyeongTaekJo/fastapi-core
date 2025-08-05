# FileService 리팩토링 + 파일 교체 (기존 row 유지하며 path 수정)

from typing import Literal, Optional

from fastapi import HTTPException
from common.const.path_consts import TEMP_FOLDER_PATH, TEMP_BACKUP_PATH
from common.file.enums.owner_type_enum import OWNER_TYPE_MAPPING
from common.file.file_utils import (
    get_file_type_by_ext,
    backup_files,
    restore_backups,
    delete_backups,
    move_temp_file_to_target,
    _extract_file_id_from_path
)
from common.file.repository import FileRepository
from sqlalchemy.ext.asyncio import AsyncSession
import os
import logging

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self, db: AsyncSession, target_folder_path: str):
        self.repo = FileRepository(db)
        self.target_folder_path = target_folder_path

    async def save_files(self, owner_type: str, owner_id: int, temp_filenames: list[str]):
        for index, filename in enumerate(temp_filenames):
            await self.move_from_temp_and_link(
                temp_filename=filename,
                owner_type=owner_type,
                owner_id=owner_id,
                is_main=(index == 0),
                order=index
            )

    async def update_files(self, owner_type: str, owner_id: int, file_payload: list[object]):
        # 기존 파일 정보 가져오기
        existing_files = await self.repo.get_files_by_owner(owner_type, owner_id)
        existing_ids = {f.id for f in existing_files}
        logger.debug(f" 기존 연결된 파일 ID들: {existing_ids}")

        try:
            # 빈 배열이면 모든 파일 삭제
            if not file_payload:
                logger.debug(" 빈 파일 배열 - 모든 파일 삭제")
                # 실제 파일 삭제
                for file in existing_files:
                    file_path = os.path.join(self.target_folder_path, file.path)
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            logger.info(f" 파일 삭제 완료: {file_path}")
                    except Exception as e:
                        logger.warning(f" 파일 삭제 실패: {file_path} - {e}")
                
                # DB에서 파일 삭제
                await self.repo.delete_files_by_ids(existing_ids)
                await self.repo.session.flush()  # 변경사항을 DB에 즉시 적용
                return

            # 파일 업데이트 처리
            received_ids = set()
            for item in file_payload:
                order = item.order

                #  기존 파일인데 새 파일로 교체
                if item.id and item.temp_file:
                    if item.id in existing_ids:
                        logger.debug(f" 교체 처리 중: {item.id}")
                        received_ids.add(item.id)
                        await self.update_existing_file_with_new_temp(
                            file_id=item.id,
                            temp_file=item.temp_file,
                            owner_type=owner_type,
                            owner_id=owner_id,
                            order=order
                        )
                    else:
                        logger.warning(f" 무시됨: item.id={item.id}는 연결된 파일이 아닙니다.")

                #  기존 파일 → 순서만 변경
                elif item.id:
                    if item.id in existing_ids:
                        logger.debug(f" 순서만 변경: {item.id}")
                        received_ids.add(item.id)
                        await self.repo.update_file_order(item.id, order)
                    else:
                        logger.warning(f" 무시됨: item.id={item.id}는 연결된 파일이 아닙니다.")

                #  새 파일 추가
                elif item.temp_file:
                    await self.move_from_temp_and_link(
                        temp_filename=item.temp_file,
                        owner_type=owner_type,
                        owner_id=owner_id,
                        is_main=(order == 0),
                        order=order
                    )

            # 삭제할 파일 ID 계산
            to_delete_ids = existing_ids - received_ids
            logger.debug(f" 삭제 대상 file ids: {to_delete_ids}")

            if to_delete_ids:
                # 삭제할 파일들의 실제 파일 삭제
                for file in existing_files:
                    if file.id in to_delete_ids:
                        file_path = os.path.join(self.target_folder_path, file.path)
                        try:
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                logger.info(f" 파일 삭제 완료: {file_path}")
                        except Exception as e:
                            logger.warning(f" 파일 삭제 실패: {file_path} - {e}")

                # DB에서 파일 삭제
                await self.repo.delete_files_by_ids(to_delete_ids)
                await self.repo.session.flush()  # 변경사항을 DB에 즉시 적용

        except Exception as e:
            logger.error(f" 파일 업데이트 중 오류 발생: {str(e)}")
            raise e

    async def update_existing_file_with_new_temp(self, file_id: int, temp_file: str, owner_type: str, owner_id: int, order: int):
        file = await self.repo.get_file_by_id(file_id)
        if not file:
            raise HTTPException(status_code=404, detail="파일이 존재하지 않습니다.")

        #  기존 파일 경로
        old_full_path = os.path.join(self.target_folder_path, file.path)

        # 신규 경로 설정
        temp_path = os.path.join(TEMP_FOLDER_PATH, temp_file)
        target_rel_path = os.path.join(owner_type, temp_file)
        target_path = os.path.join(self.target_folder_path, target_rel_path)

        if not os.path.exists(temp_path):
            raise FileNotFoundError("임시 파일이 존재하지 않습니다.")

        #  temp → target으로 복사
        move_temp_file_to_target(temp_path, target_path)
        self.record_moved_file(temp_path, target_path)

        #  기존 파일 삭제
        if os.path.exists(old_full_path):
            try:
                os.remove(old_full_path)
                logger.info(f" 기존 파일 삭제 완료: {old_full_path}")
            except Exception as e:
                logger.warning(f" 기존 파일 삭제 실패: {old_full_path} - {e}")

        # DB 업데이트
        file.path = target_rel_path
        file.original_name = temp_file
        file.size = os.path.getsize(target_path)
        file.order = order
        file.type = get_file_type_by_ext(temp_file)

        await self.repo.session.flush()

    async def move_from_temp_and_link(
        self,
        temp_filename: str,
        owner_type: str,
        owner_id: int,
        description: Optional[str] = None,
        is_main: bool = False,
        order: int = 0
    ):
        subfolder = owner_type
        target_rel_path = os.path.join(subfolder, temp_filename)
        temp_path = os.path.join(TEMP_FOLDER_PATH, temp_filename)
        target_path = os.path.join(self.target_folder_path, target_rel_path)

        try:
            if not os.path.exists(temp_path):
                raise FileNotFoundError("임시 파일이 존재하지 않습니다.")

            move_temp_file_to_target(temp_path, target_path)
            self.record_moved_file(temp_path, target_path)

            file_type = get_file_type_by_ext(temp_filename)
            size = os.path.getsize(target_path)
            mapping_field = OWNER_TYPE_MAPPING.get(owner_type)

            await self.repo.create_file_record(
                path=target_rel_path,
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

        except Exception as e:
            if (temp_path, target_path) in getattr(self, "_moved_files", []):
                move_temp_file_to_target(target_path, temp_path)
            raise HTTPException(status_code=500, detail={
                "error": "FILE_SAVE_FAILED",
                "message": "파일 저장 중 오류 발생. 롤백되었습니다.",
                "reason": str(e),
            })

    async def prepare_for_save_or_update(self, owner_type: str, owner_id: int):
        existing_files = await self.repo.get_files_by_owner(owner_type, owner_id)
        self._backups = backup_files([f.path for f in existing_files], self.target_folder_path, TEMP_BACKUP_PATH)
        self._old_files = existing_files
        self._old_file_ids = {f.id for f in existing_files}

        logger.debug(f" old_files: {[f.id for f in existing_files]}")

    async def rollback(self):
        if hasattr(self, "_moved_files"):
            for temp_path, target_path in reversed(self._moved_files):
                if os.path.exists(target_path):
                    move_temp_file_to_target(target_path, temp_path)
        if hasattr(self, "_backups"):
            restore_backups(self._backups)

    def record_moved_file(self, src: str, dest: str):
        if not hasattr(self, "_moved_files"):
            self._moved_files = []
        self._moved_files.append((src, dest))

    async def collect_file_paths(self, owner_type: str, owner_id: int) -> list[str]:
        files = await self.get_files_by_owner(owner_type, owner_id)
        return [os.path.join(self.target_folder_path, f.path) for f in files]
    
    async def get_files_by_owner(self, owner_type: str, owner_id: int):
        return await self.repo.get_files_by_owner(owner_type, owner_id)
