# post/image/image_service.py

from common.image.service import ImageService
from common.image.enums.image_type_enum import ImageModelType
from common.const.path_consts import POST_IMAGE_PATH

class PostImageService:
    def __init__(self):
        self.image_service = ImageService(
            image_type=ImageModelType.POST_IMAGE,
            image_path_root=POST_IMAGE_PATH  # 이름 정확하게
        )

    async def save_images(self, post_id: int, image_paths: list[str]):
        await self.image_service.save_images(target_id=post_id, image_paths=image_paths)

    async def update_images(self, post_id: int, image_paths: list[str]):
        await self.image_service.update_images(target_id=post_id, image_paths=image_paths)

    async def delete_images(self, post_id: int):
        await self.image_service.repo.delete_images_by_target_id(post_id)

    # async def get_images(self, post_id: int):
    #     return await self.image_service.repo.get_images_by_target_id(post_id)
