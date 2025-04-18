from sqlalchemy import select, delete
from common.image.model import ImageModel
from database.session_context import get_db_from_context

class ImageRepository:
    async def create_image(self, **kwargs) -> ImageModel:
        session = get_db_from_context()
        image = ImageModel(**kwargs)
        session.add(image)
        await session.flush()
        await session.refresh(image)
        return image

    async def delete_images_by_target_id(self, target_id: int) -> list[str]:
        session = get_db_from_context()

        result = await session.execute(
            select(ImageModel.path).where(ImageModel.post_id == target_id)
        )
        paths_to_delete = result.scalars().all()

        await session.execute(
            delete(ImageModel).where(ImageModel.post_id == target_id)
        )

        return paths_to_delete
