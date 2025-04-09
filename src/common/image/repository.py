from sqlalchemy import select, delete
from common.image.model import ImageModel
from database.session_context import get_db_from_context

class ImageRepository:
    def __init__(self):
        self.session = get_db_from_context()

    async def create_image(self, **kwargs) -> ImageModel:
        image = ImageModel(**kwargs)
        self.session.add(image)
        await self.session.flush()
        await self.session.refresh(image)
        return image

    async def delete_images_by_target_id(self, target_id: int) -> list[str]:
        result = await self.session.execute(
            select(ImageModel.path).where(ImageModel.post_id == target_id)
        )
        paths_to_delete = result.scalars().all()

        await self.session.execute(
            delete(ImageModel).where(ImageModel.post_id == target_id)
        )

        return paths_to_delete
