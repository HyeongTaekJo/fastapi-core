import os
import logging
from common.file.file_service import FileService

logger = logging.getLogger(__name__)

class FileCleaner:
    def __init__(self, file_service: FileService):
        self.file_service = file_service

    async def remove_all_files_for(self, owner_type: str, owner_id: int):
        files = await self.file_service.get_files_by_owner(owner_type, owner_id)
        paths = [
            os.path.join(self.file_service.target_folder_path, f.path)
            for f in files
        ]

        for path in paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    logger.info(f"🔌 파일 삭제 완료: {path}")
                except Exception as e:
                    logger.warning(f"⚠️ 파일 삭제 실패: {path} - {e}")

# 사용예
# await FileCleaner(file_service).remove_all_files_for("post", post_id)
