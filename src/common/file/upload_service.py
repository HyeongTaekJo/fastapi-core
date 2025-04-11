import uuid
import aiofiles
import os
from pathlib import Path
from fastapi import UploadFile, HTTPException
from common.file.file_utils import get_file_type_by_ext, validate_file
from common.const.path_consts import TEMP_FOLDER_PATH
from cache.redis_connection import redis  # ✅ Redis 인스턴스 import

class UploadService:
    @staticmethod
    async def save_temp_file(file: UploadFile) -> str:
        try:
            validate_file(file)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        ext = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(TEMP_FOLDER_PATH, unique_filename)
        os.makedirs(TEMP_FOLDER_PATH, exist_ok=True)

        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)

        # ✅ Redis에 TTL 설정 (1시간)
        await redis.setex(f"temp_file:{unique_filename}", 3600, "1")

        return unique_filename
