from pydantic import BaseModel, EmailStr
from typing import Optional

#  로그인 응답 스키마
class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str

