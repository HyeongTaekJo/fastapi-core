# 📄 post/file/file_service.py

from common.file.file_service import FileService
from common.const.path_consts import FILE_UPLOAD_PATH


class PostFileService:
    """
    Post에 연결된 파일을 처리하는 도메인 전용 서비스

    - temp 파일 이동 및 DB 연결
    - 삭제
    - 조회
    """

    def __init__(self):
        self.file_service = FileService(target_folder_path=FILE_UPLOAD_PATH)

    async def save_files(self, post_id: int, temp_filenames: list[str]):
        """
        임시 파일들을 실제 경로로 이동하고 DB에 연결
        """
        for filename in temp_filenames:
            await self.file_service.move_from_temp_and_link(
                temp_filename=filename,
                owner_type="post",
                owner_id=post_id
            )

    async def delete_files(self, post_id: int):
        """
        해당 post에 연결된 모든 파일을 삭제 (DB + 디스크)
        """
        await self.file_service.delete_by_owner(
            owner_type="post",
            owner_id=post_id
        )

    async def get_files(self, post_id: int):
        """
        해당 post에 연결된 파일들을 조회
        """
        return await self.file_service.get_files_by_owner(
            owner_type="post",
            owner_id=post_id
        )
