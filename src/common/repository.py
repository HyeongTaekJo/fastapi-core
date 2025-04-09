from sqlalchemy import insert, delete
from fastapi import HTTPException, status
from typing import List
from common.model.image_model import ImageModel
from database.session_context import get_db_from_context  # Context 기반 세션 주입
import os
from sqlalchemy import select, delete
import logging
from common.const.path_consts import POST_IMAGE_PATH


logger = logging.getLogger(__name__)

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
    
    async def delete_images_by_post_id(self, post_id: int) -> list[str]:
        # 1. 삭제할 이미지 경로 조회
        result = await self.session.execute(
            select(ImageModel.path).where(ImageModel.post_id == post_id)
        )
        paths_to_delete = result.scalars().all()

        # 2. DB에서 레코드 삭제
        await self.session.execute(
            delete(ImageModel).where(ImageModel.post_id == post_id)
        )

        # 3. 디스크 삭제는 서비스 레이어에서 처리하므로 생략
        return paths_to_delete  # 💡 삭제할 파일 경로들 반환
