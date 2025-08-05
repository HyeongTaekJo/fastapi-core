from typing import List
from sqlalchemy import select, delete
from user.model import UserModel
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_users(self) -> List[UserModel]:
        result = await self.db.scalars(select(UserModel))
        return list(result)

    async def get_user_by_email(self, email: str) -> UserModel | None:
        return await self.db.scalar(select(UserModel).where(UserModel.email == email))

    async def get_user_by_field(self, field: str, value: Any) -> UserModel | None:
        if not hasattr(UserModel, field):
            raise ValueError(f"UserModel에 존재하지 않는 필드입니다: {field}")
        column = getattr(UserModel, field)
        return await self.db.scalar(select(UserModel).where(column == value))

    async def get_user_by_id(self, id: int) -> UserModel | None:
        return await self.db.scalar(select(UserModel).where(UserModel.id == id))

    async def create_user(self, new_user: UserModel) -> UserModel:
        self.db.add(new_user)
        await self.db.flush()
        await self.db.refresh(new_user)
        return new_user
