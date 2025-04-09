from fastapi import HTTPException
from common.image.repository import ImageRepository
from common.image.utils import backup_files, restore_backups, delete_backups, move_temp_file_to_target
from common.const.path_consts import TEMP_FOLDER_PATH, TEMP_BACKUP_PATH
from post.image.schemas.request import CreatePostImageSchema
from common.image.model import ImageModelType
from os.path import join, exists
from shutil import move


class ImageService:
    def __init__(self, image_type: ImageModelType, image_path_root: str):
        self.repo = ImageRepository()
        self.image_type = image_type
        self.image_path_root = image_path_root

    async def sync_images(self, target_id: int, image_paths: list[str], delete_existing: bool = False):
        backup_files_list = []
        moved_files = []

        try:
            if delete_existing:
                old_paths = await self.repo.delete_images_by_target_id(target_id)
                backup_files_list = backup_files(old_paths, self.image_path_root, TEMP_BACKUP_PATH)

            for index, rel_path in enumerate(image_paths):
                temp_path = join(TEMP_FOLDER_PATH, rel_path)
                target_path = join(self.image_path_root, rel_path)

                if not exists(temp_path):
                    raise HTTPException(status_code=400, detail="존재하지 않는 이미지입니다.")

                image_schema = CreatePostImageSchema(
                    post_id=target_id,
                    path=rel_path,
                    order=index,
                    type=self.image_type
                )

                await self.repo.create_image(**image_schema.model_dump())
                move_temp_file_to_target(temp_path, target_path)
                moved_files.append((temp_path, target_path))

            delete_backups(backup_files_list)

        except Exception as e:
            for temp, final in moved_files:
                if exists(final):
                    move(final, temp)
            restore_backups(backup_files_list)

            raise HTTPException(
                status_code=500,
                detail={
                    "error": "IMAGE_UPDATE_FAILED",
                    "message": "이미지 업데이트 중 오류 발생. 롤백 수행됨.",
                    "reason": str(e)
                }
            )

    async def save_images(self, target_id: int, image_paths: list[str]):
        await self.sync_images(target_id, image_paths, delete_existing=False)

    async def update_images(self, target_id: int, image_paths: list[str]):
        await self.sync_images(target_id, image_paths, delete_existing=True)
