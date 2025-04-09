# ✅ 수정된 파일: common/file/file_service.py

import os
from shutil import move
from pathlib import Path
from common.file.repository import FileRepository
from common.const.path_consts import TEMP_FOLDER_PATH
from common.file.file_utils import get_file_type_by_ext
from common.file.enums.owner_type_enum import OWNER_TYPE_MAPPING

class FileService:
    def __init__(self, target_folder_path: str):
        self.repo = FileRepository()
        self.target_folder_path = target_folder_path  # ✅ 주입받은 경로 저장

    async def move_from_temp_and_link(
        self,
        temp_filename: str,
        owner_type: str,
        owner_id: int,
        description: str | None = None,
        is_main: bool = False,
    ):
        temp_path = os.path.join(TEMP_FOLDER_PATH, temp_filename)
        new_path = os.path.join(self.target_folder_path, temp_filename)  # ✅ 수정

        if not os.path.exists(temp_path):
            raise FileNotFoundError("임시 파일이 존재하지 않습니다.")

        os.makedirs(self.target_folder_path, exist_ok=True)
        move(temp_path, new_path)

        file_type = get_file_type_by_ext(temp_filename)
        size = os.path.getsize(new_path)

        # owner_type에 맞는 모델 ID 필드를 동적으로 매핑
        mapping_field = OWNER_TYPE_MAPPING.get(owner_type)
        if not mapping_field:
            raise ValueError(f"Invalid owner type: {owner_type}")

        # 해당 모델에 맞는 ID 필드를 동적으로 전달
        return await self.repo.create_file_record(
            path=temp_filename,
            original_name=temp_filename,
            size=size,
            type=file_type,
            is_main=is_main,
            description=description,
            owner_type=owner_type,
            owner_id=owner_id,
            **{mapping_field: owner_id}  # 동적으로 매핑된 ID 필드 추가
        )

    async def delete_by_owner(self, owner_type: str, owner_id: int):
        files = await self.repo.get_files_by_owner(owner_type, owner_id)

        for file in files:
            full_path = os.path.join(self.target_folder_path, file.path)
            if os.path.exists(full_path):
                os.remove(full_path)

        await self.repo.delete_files_by_owner(owner_type, owner_id)

    async def get_files_by_owner(self, owner_type: str, owner_id: int):
        return await self.repo.get_files_by_owner(owner_type, owner_id)
