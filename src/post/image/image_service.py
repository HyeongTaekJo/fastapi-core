from shutil import move
from os.path import join, exists
from common.const.path_consts import TEMP_FOLDER_PATH, POST_IMAGE_PATH, TEMP_BACKUP_PATH
from common.model.image_model import ImageModelType
from fastapi import HTTPException, status
from common.repository import CommonRepository
from post.image.schemas.request import CreatePostImageSchema
from database.session_context import get_db_from_context
from typing import List
import os
from os.path import join, exists, dirname
from shutil import move
import logging

logger = logging.getLogger(__name__)


class PostImageService:
    def __init__(self):
        # 미들웨어에서 설정한 Context 기반 세션을 사용
        self.session = get_db_from_context()
        self.common_repo = CommonRepository()  # repo도 내부에서 context 기반 세션 사용

    async def sync_post_images(
        self,
        post_id: int,
        image_paths: list[str],
        delete_existing: bool = False
    ):
        backup_files = []  # (original_path, backup_path)
        moved_files = []   # (temp_path, new_path)

        try:
            # 1. 기존 이미지 삭제 처리
            if delete_existing:
                # 기존 이미지 경로 조회 + DB 레코드 삭제
                old_image_paths = await self.common_repo.delete_images_by_post_id(post_id)

                for path in old_image_paths:
                    original_path = join(POST_IMAGE_PATH, path)
                    backup_path = join(TEMP_BACKUP_PATH, path)

                    if exists(original_path):
                        os.makedirs(dirname(backup_path), exist_ok=True)
                        move(original_path, backup_path)
                        backup_files.append((original_path, backup_path))
                        logger.info(f"🔄 기존 이미지 백업됨: {original_path} → {backup_path}")

            # 2. 새 이미지 추가
            for index, image_path in enumerate(image_paths):
                temp_path = join(TEMP_FOLDER_PATH, image_path)
                new_path = join(POST_IMAGE_PATH, image_path)

                if not exists(temp_path):
                    raise HTTPException(status_code=400, detail="존재하지 않는 이미지입니다.")

                image_schema = CreatePostImageSchema(
                    post_id=post_id,
                    path=image_path,
                    order=index,
                    type=ImageModelType.POST_IMAGE
                )

                await self.common_repo.create_image(**image_schema.model_dump())

                os.makedirs(dirname(new_path), exist_ok=True)
                move(temp_path, new_path)
                moved_files.append((temp_path, new_path))
                logger.info(f"✅ 새 이미지 이동 완료: {temp_path} → {new_path}")

            # 3. 성공 시 → 백업 이미지 완전 삭제
            for _, backup_path in backup_files:
                if exists(backup_path):
                    os.remove(backup_path)
                    logger.info(f"🗑️ 백업 이미지 삭제됨: {backup_path}")

        except Exception as e:
            # 4. 예외 발생 시 롤백
            for temp_path, new_path in moved_files:
                if exists(new_path):
                    move(new_path, temp_path)
                    logger.warning(f"⛔ 새 이미지 롤백됨: {new_path} → {temp_path}")

            for original_path, backup_path in backup_files:
                if exists(backup_path):
                    move(backup_path, original_path)
                    logger.warning(f"⛔ 백업 이미지 복원됨: {backup_path} → {original_path}")

            logger.error(f"❌ 이미지 업데이트 중 예외 발생: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "IMAGE_UPDATE_FAILED",
                    "message": "이미지 업데이트 중 오류가 발생하여 복구했습니다.",
                    "reason": str(e)
                }
            )

    # create 용도로 사용
    async def save_post_images(self, post_id: int, image_paths: list[str]):
        await self.sync_post_images(post_id, image_paths, delete_existing=False)

    # update 용도로 사용
    async def update_post_images(self, post_id: int, image_paths: list[str]):
        await self.sync_post_images(post_id, image_paths, delete_existing=True)