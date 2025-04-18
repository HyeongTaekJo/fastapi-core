from typing import List
from sqlalchemy import select, delete
from user.model import UserModel
from database.session_context import get_db_from_context  # Context 기반으로 변경
from typing import Any

class UserRepository:
    async def get_users(self) -> List[UserModel]:
        session = get_db_from_context()
        result = await session.scalars(select(UserModel))
        return list(result)

    async def get_user_by_email(self, email: str) -> UserModel | None:
        session = get_db_from_context()
        return await session.scalar(select(UserModel).where(UserModel.email == email))
    
    async def get_user_by_field(self, field: str, value: Any) -> UserModel | None:
        session = get_db_from_context()
        if not hasattr(UserModel, field):
            raise ValueError(f"UserModel에 존재하지 않는 필드입니다: {field}")
        column = getattr(UserModel, field)
        return await session.scalar(select(UserModel).where(column == value))

    async def get_user_by_id(self, id: int) -> UserModel | None:
        session = get_db_from_context()
        return await session.scalar(select(UserModel).where(UserModel.id == id))
    
    async def create_user(self, new_user: UserModel) -> UserModel:
        """DB에 사용자 추가"""
        session = get_db_from_context()
        session.add(new_user)
        # await session.commit() ❌ 트랜잭션은 서비스나 라우터에서 처리
        await session.flush()
        await session.refresh(new_user)
        return new_user
