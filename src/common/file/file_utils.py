import os
from mimetypes import guess_type
from pathlib import Path
from common.file.file_enum import FileModelType

# 확장자 기준 구분
ALLOWED_FILE_TYPES = {
    FileModelType.IMAGE: {".jpg", ".jpeg", ".png"},
    FileModelType.PDF: {".pdf"},
    FileModelType.EXCEL: {".xls", ".xlsx"},
    FileModelType.PPT: {".ppt", ".pptx"},
    FileModelType.WORD: {".doc", ".docx"},
    FileModelType.HWP: {".hwp"},
    FileModelType.OTHER: set()
}

MAX_UPLOAD_FILE_SIZE_MB = 10

def get_file_type_by_ext(filename: str) -> FileModelType:
    ext = Path(filename).suffix.lower()
    for file_type, extensions in ALLOWED_FILE_TYPES.items():
        if ext in extensions:
            return file_type
    return FileModelType.OTHER

def validate_file(file) -> None:
    ext = Path(file.filename).suffix.lower()
    file_type = get_file_type_by_ext(file.filename)
    if file_type == FileModelType.OTHER:
        raise ValueError("지원하지 않는 파일 형식입니다.")

    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_UPLOAD_FILE_SIZE_MB * 1024 * 1024:
        raise ValueError("파일 크기가 너무 큽니다.")
