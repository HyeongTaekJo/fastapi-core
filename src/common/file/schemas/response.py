from pydantic import BaseModel, field_validator
from typing import Optional
from common.file.file_enum import FileModelType
from datetime import datetime

class FileSchema(BaseModel):
    id: int
    path: str
    original_name: str
    size: int
    type: FileModelType
    description: Optional[str] = None
    is_main: bool
    created_at: Optional[str] = None

    # Pydantic 2.x에서는 field_validator로 사용
    @field_validator('created_at', mode='before')
    def convert_datetime_to_string(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()  # datetime을 ISO 8601 형식으로 변환
        return v

    class Config:
        from_attributes = True
