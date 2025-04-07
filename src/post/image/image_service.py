from shutil import move
from os.path import join, exists
from common.const.path_consts import TEMP_FOLDER_PATH, POST_IMAGE_PATH
from common.model.image_model import ImageModelType
from fastapi import HTTPException, status
from common.repository import CommonRepository
from post.image.schemas.request import CreatePostImageSchema

class PostImageService:
    def __init__(self):
        self.common_repo = CommonRepository()  # repo도 내부에서 context 기반 세션 사용

    async def create_post_image(
        self,
        request: CreatePostImageSchema
    ):
        temp_path = join(TEMP_FOLDER_PATH, request.path)
        new_path = join(POST_IMAGE_PATH, request.path)

        if not exists(temp_path):
            raise HTTPException(status_code=400, detail="존재하지 않는 이미지입니다.")

        # 이미지 저장
        image = await self.common_repo.create_image(**request.model_dump())

        # 임시 -> 실제 경로로 이동
        move(temp_path, new_path)

        return image
