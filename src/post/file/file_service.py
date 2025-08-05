from common.file.file_service import FileService
from common.const.path_consts import FILE_UPLOAD_PATH, TEMP_FOLDER_PATH
import os
from sqlalchemy.ext.asyncio import AsyncSession

class PostFileService:
    def __init__(self, db: AsyncSession):
        self.file_service = FileService(db, target_folder_path=FILE_UPLOAD_PATH)

    async def save_files(self, post_id: int, temp_filenames: list[str]):
        await self.file_service.save_files("post", post_id, temp_filenames)

    async def update_files(self, post_id: int, file_payload: list[dict]):
        await self.file_service.update_files("post", post_id, file_payload)

    async def delete_files(self, post_id: int):
        await self.file_service.delete_by_owner("post", post_id)

    async def get_files(self, post_id: int):
        return await self.file_service.get_files_by_owner("post", post_id)
