from fastapi import APIRouter, UploadFile, File
from common.image.upload_service import ImageUploadService

router = APIRouter(prefix="/common/image", tags=["Common"])

@router.post("")
async def upload_image(image: UploadFile = File(...)):
    filename = await ImageUploadService.save_temp_image(image)
    return {"fileName": filename}
