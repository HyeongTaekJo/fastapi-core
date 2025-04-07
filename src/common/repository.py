from sqlalchemy import insert
from fastapi import HTTPException, status
from typing import List
from common.model.image_model import ImageModel
from common.utils.db_context import get_db_from_context  # Context 기반 세션 주입

class CommonRepository:
    def __init__(self):
        # 미들웨어에서 주입한 세션을 ContextVar에서 꺼냄
        self.session = get_db_from_context()

    async def create_image(self, **kwargs) -> ImageModel:
        # kwargs에는 모델의 맞는 객체데이터가 들어 있다.
        # post 모델인 경우 → post_id, order, path, type 등 포함
        image = ImageModel(**kwargs)
        self.session.add(image)
        await self.session.flush()
        await self.session.refresh(image)  # 데이터베이스에서 다시 읽어옴 → id 포함
        return image
