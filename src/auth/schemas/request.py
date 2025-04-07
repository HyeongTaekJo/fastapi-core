from pydantic import BaseModel, EmailStr
from typing import Optional


#  회원가입 요청 스키마
class RegisterUserSchema(BaseModel):
    nickname: str
    email: EmailStr
    password: str
    


#  로그인 요청 스키마
class LoginUserSchema(BaseModel):
    email: EmailStr
    password: str

# 토큰 검증
class UserTokenSchema(BaseModel):
    id: int
    email: str
    