# post/image/image_service.py

from common.image.service import ImageService
from common.image.model import ImageModelType
from common.const.path_consts import POST_IMAGE_PATH

class PostImageService:
    def __init__(self):
        self.image_service = ImageService(ImageModelType.POST_IMAGE, POST_IMAGE_PATH)

    async def save_images(self, post_id: int, image_paths: list[str]):
        await self.image_service.save_images(post_id, image_paths)

    async def update_images(self, post_id: int, image_paths: list[str]):
        await self.image_service.update_images(post_id, image_paths)
