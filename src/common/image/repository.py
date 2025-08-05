from sqlalchemy import select, delete
from common.image.model import ImageModel
from sqlalchemy.ext.asyncio import AsyncSession

class ImageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    async def create_image(self, **kwargs) -> ImageModel:
        image = ImageModel(**kwargs)
        self.db.add(image)
        await self.db.flush()
        await self.db.refresh(image)
        return image

    async def delete_images_by_target_id(self, target_id: int) -> list[str]:

        result = await self.db.execute(
            select(ImageModel.path).where(ImageModel.post_id == target_id)
        )
        paths_to_delete = result.scalars().all()

        await self.db.execute(
            delete(ImageModel).where(ImageModel.post_id == target_id)
        )

        return paths_to_delete
