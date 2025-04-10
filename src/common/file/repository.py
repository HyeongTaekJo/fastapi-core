
from common.file.file_model import FileModel
from database.session_context import get_db_from_context
from sqlalchemy import select, delete

import logging

logger = logging.getLogger(__name__)

class FileRepository:
    def __init__(self):
        self.session = get_db_from_context()

    async def create_file_record(self, **kwargs) -> FileModel:

        logger.debug(f"✅ create_file_record() with kwargs={...}")

        file = FileModel(**kwargs)
        self.session.add(file)
        await self.session.flush()
        await self.session.refresh(file)
        return file
    
    async def get_files_by_owner(self, owner_type: str, owner_id: int):
        stmt = select(FileModel).where(
            FileModel.owner_type == owner_type,
            FileModel.owner_id == owner_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_files_by_owner(self, owner_type: str, owner_id: int):
        await self.session.execute(
            delete(FileModel).where(
                FileModel.owner_type == owner_type,
                FileModel.owner_id == owner_id
            )
        )

    async def delete_files_by_ids(self, ids: set[int]):
        if not ids:
            return
        await self.session.execute(
            delete(FileModel).where(FileModel.id.in_(ids))
        )
    

#     ✅ 마무리 체크리스트
# 항목	상태
# ✔ 범용 파일 타입 Enum	✅ 완료
# ✔ 유효성 검사 및 사이즈 체크	✅ 완료
# ✔ TEMP → 실제 폴더 이동	✅ 완료
# ✔ owner_type, owner_id 연결	✅ 완료
# ✔ Post 외 모델 대응 가능	✅ 완료
# ✔ 확장성 있는 모델 구성	✅ 완료
# ✔ 대표 여부, 설명, 업로드 시간	✅ 완료