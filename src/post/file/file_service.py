# 📄 post/file/file_service.py

from common.file.file_service import FileService
from common.const.path_consts import FILE_UPLOAD_PATH, TEMP_FOLDER_PATH
import os


class PostFileService:
    def __init__(self):
        self.file_service = FileService(target_folder_path=FILE_UPLOAD_PATH)

    async def create_files(self, post_id: int, temp_filenames: list[str]):
        await self.file_service.save_files("post", post_id, temp_filenames, replace=False)

    async def update_files(self, post_id: int, temp_filenames: list[str]):
        await self.file_service.save_files("post", post_id, temp_filenames, replace=True)

    async def delete_files(self, post_id: int):
        await self.file_service.delete_by_owner("post", post_id)

    async def get_files(self, post_id: int):
        return await self.file_service.get_files_by_owner("post", post_id)

    async def collect_file_paths(self, post_id: int) -> list[str]:
        files = await self.file_service.get_files_by_owner("post", post_id)
        return [os.path.join(self.file_service.target_folder_path, f.path) for f in files]