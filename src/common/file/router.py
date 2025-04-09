from fastapi import APIRouter, UploadFile, File
from common.file.upload_service import UploadService

router = APIRouter(prefix="/common/files", tags=["Files"])

@router.post("")
async def upload_file(file: UploadFile = File(...)):
    filename = await UploadService.save_temp_file(file)
    return {"fileName": filename}
