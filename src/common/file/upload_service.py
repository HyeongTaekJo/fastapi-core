import uuid
import aiofiles
import os
from pathlib import Path
from fastapi import UploadFile, HTTPException
from common.file.file_utils import get_file_type_by_ext, validate_file
from common.const.path_consts import TEMP_FOLDER_PATH
from cache.redis_connection import redis
import logging
from typing import List

logger = logging.getLogger(__name__)

class UploadService:
    @staticmethod
    async def save_temp_file(file: UploadFile) -> str:
        try:
            # 파일이 비어있는지 체크
            if not file.filename:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "NO_FILES_UPLOADED",
                        "message": "파일이 업로드되지 않았습니다. 최소 1개 이상의 파일을 업로드해주세요.",
                        "status_code": 400
                    }
                )

            # 파일 검증
            validate_file(file)
            
            # 파일 확장자 추출
            ext = Path(file.filename).suffix.lower()
            if not ext:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "NO_FILE_EXTENSION",
                        "message": "파일 확장자가 없습니다.",
                        "status_code": 400
                    }
                )
                
            # 고유한 파일명 생성
            unique_filename = f"{uuid.uuid4()}{ext}"
            file_path = os.path.join(TEMP_FOLDER_PATH, unique_filename)
            
            # 임시 폴더 생성
            os.makedirs(TEMP_FOLDER_PATH, exist_ok=True)
            
            # 파일 저장
            try:
                async with aiofiles.open(file_path, "wb") as out_file:
                    content = await file.read()
                    await out_file.write(content)
                logger.info(f"✅ 임시 파일 저장 성공: {unique_filename}")
            except Exception as e:
                logger.error(f"❌ 파일 저장 실패: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail={
                        "code": "FILE_SAVE_FAILED",
                        "message": "파일 저장에 실패했습니다.",
                        "status_code": 500
                    }
                )
            
            # Redis에 TTL 설정 (1시간)
            await redis.setex(f"temp_file:{unique_filename}", 3600, "1")
            
            return unique_filename
            
        except ValueError as e:
            logger.error(f"❌ 파일 검증 실패: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_FILE_TYPE",
                    "message": str(e),
                    "status_code": 400
                }
            )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            logger.error(f"❌ 예상치 못한 오류: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail={
                    "code": "UNEXPECTED_ERROR",
                    "message": str(e),
                    "status_code": 500
                }
            )
