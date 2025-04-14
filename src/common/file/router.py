from fastapi import APIRouter, UploadFile, File
from typing import List
from common.file.upload_service import UploadService

router = APIRouter(prefix="/common/files", tags=["Files"])

@router.post("")
async def upload_files(files: List[UploadFile] = File(None)):
    filenames = []
    for file in files:
        filename = await UploadService.save_temp_file(file)
        filenames.append(filename)
    return {"fileNames": filenames}
