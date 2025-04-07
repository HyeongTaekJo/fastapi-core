from fastapi import APIRouter, UploadFile, File
from common.service import CommonService

router = APIRouter(prefix="/common", tags=["Common"])

@router.post("/image")
async def upload_image(image: UploadFile = File(...)):
    filename = await CommonService.save_temp_image(image)
    return {"fileName": filename}
