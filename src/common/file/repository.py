from common.file.file_model import FileModel
from database.session_context import get_db_from_context
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

import logging

logger = logging.getLogger(__name__)

class FileRepository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session  # 외부에서 세션 주입 시 사용

    async def create_file_record(self, **kwargs) -> FileModel:
        logger.debug(f"✅ create_file_record() with kwargs={...}")
        session = self.session or get_db_from_context()

        file = FileModel(**kwargs)
        session.add(file)
        await session.flush()
        await session.refresh(file)
        return file
    
    async def get_files_by_owner(self, owner_type: str, owner_id: int):
        session = self.session or get_db_from_context()

        stmt = select(FileModel).where(
            FileModel.owner_type == owner_type,
            FileModel.owner_id == owner_id
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def delete_files_by_owner(self, owner_type: str, owner_id: int):
        session = self.session or get_db_from_context()

        await session.execute(
            delete(FileModel).where(
                FileModel.owner_type == owner_type,
                FileModel.owner_id == owner_id
            )
        )

    async def delete_files_by_ids(self, ids: set[int]):
        if not ids:
            return
        session = self.session or get_db_from_context()

        await session.execute(
            delete(FileModel).where(FileModel.id.in_(ids))
        )
        await session.flush()

    async def get_file_by_uuid(self, uuid: str) -> Optional[FileModel]:
        session = self.session or get_db_from_context()

        stmt = select(FileModel).where(FileModel.original_name.like(f"%{uuid}%"))
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    # 전체 파일 경로만 가져오는 메서드
    async def get_all_file_paths(self) -> list[str]:
        session = self.session or get_db_from_context()

        stmt = select(FileModel.path)
        result = await session.execute(stmt)
        return [row[0] for row in result.all()]
    
    async def update_file_order(self, file_id: int, order: int):
        session = self.session or get_db_from_context()

        stmt = select(FileModel).where(FileModel.id == file_id)
        result = await session.execute(stmt)
        file = result.scalar_one_or_none()
        if file:
            file.order = order
            await session.flush()

    async def get_file_by_id(self, file_id: int) -> FileModel:
        session = self.session or get_db_from_context()

        stmt = select(FileModel).where(FileModel.id == file_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


#     ✅ 마무리 체크리스트
# 항목	상태
# ✔ 범용 파일 타입 Enum	✅ 완료
# ✔ 유효성 검사 및 사이즈 체크	✅ 완료
# ✔ TEMP → 실제 폴더 이동	✅ 완료
# ✔ owner_type, owner_id 연결	✅ 완료
# ✔ Post 외 모델 대응 가능	✅ 완료
# ✔ 확장성 있는 모델 구성	✅ 완료
# ✔ 대표 여부, 설명, 업로드 시간	✅ 완료
