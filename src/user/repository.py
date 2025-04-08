from typing import List
from sqlalchemy import select, delete
from user.model.model import UserModel
from database.session_context import get_db_from_context  # Context 기반으로 변경
from typing import Any

class UserRepository:
    def __init__(self):
        self.session = get_db_from_context()

    async def get_users(self) -> List[UserModel]:
        result = await self.session.scalars(select(UserModel))
        return list(result)

    async def get_user_by_email(self, email: str) -> UserModel | None:
        return await self.session.scalar(select(UserModel).where(UserModel.email == email))
    
    async def get_user_by_field(self, field: str, value: Any) -> UserModel | None:
        if not hasattr(UserModel, field):
            raise ValueError(f"UserModel에 존재하지 않는 필드입니다: {field}")
        column = getattr(UserModel, field)
        return await self.session.scalar(select(UserModel).where(column == value))

    async def get_user_by_id(self, id: int) -> UserModel | None:
        return await self.session.scalar(select(UserModel).where(UserModel.id == id))
    

    async def create_user(self, new_user: UserModel) -> UserModel:
        """DB에 사용자 추가"""
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user
