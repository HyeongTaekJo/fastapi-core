from pydantic import BaseModel, field_validator, field_serializer
from typing import Optional
from common.file.enums.file_model_type_enum import FileModelType
from datetime import datetime
from common.const.path_consts import FILE_PUBLIC_PATH  #  "/static/files" 와 같은 경로

class FileSchema(BaseModel):
    id: int
    path: str
    original_name: str
    size: int
    type: FileModelType
    description: Optional[str] = None
    is_main: bool
    order: int 
    created_at: Optional[str] = None

    # 날짜 문자열로 변환
    @field_validator('created_at', mode='before')
    def convert_datetime_to_string(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    # path 직렬화: 파일 접근 가능한 URL로 변환
    @field_serializer("path")
    def serialize_path(self, path: str, _info) -> str:
        return f"/{FILE_PUBLIC_PATH}/{path}".replace("\\", "/")

    class Config:
        from_attributes = True
