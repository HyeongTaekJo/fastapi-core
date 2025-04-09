import os
import uuid
from pathlib import Path
import aiofiles
from fastapi import UploadFile, HTTPException, status
from common.const.path_consts import TEMP_FOLDER_PATH
from common.const.file_consts import ALLOWED_IMAGE_EXTENSIONS
from cache.redis_connection import redis

class ImageUploadService:
    @staticmethod
    async def save_temp_image(file: UploadFile) -> str:
        ext = Path(file.filename).suffix.lower()

        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="jpg/jpeg/png 파일만 업로드 가능합니다."
            )

        os.makedirs(TEMP_FOLDER_PATH, exist_ok=True)

        filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(TEMP_FOLDER_PATH, filename)

        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)

        await redis.set(f"temp_img:{filename}", 1, ex=3600)

        return filename
