from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator
from typing import Optional

# 회원가입 요청 스키마
class RegisterUserSchema(BaseModel):
    email: Optional[EmailStr] = Field(default=None)
    login_id: Optional[str] = Field(default=None, min_length=4, max_length=30)
    phone: Optional[str] = Field(default=None, min_length=10, max_length=20)
    nickname: str
    password: str

    @model_validator(mode="after")
    def at_least_one_identifier(cls, values):
        if not (values.email or values.login_id or values.phone):
            raise ValueError("email, login_id, phone 중 하나는 반드시 입력해야 합니다.")
        return values
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if "-" in value:
            raise ValueError("전화번호는 '-' 없이 숫자만 입력해주세요.")
        if not value.isdigit():
            raise ValueError("전화번호는 숫자만 입력해주세요.")
        return value

#  로그인 요청 스키마
class LoginUserSchema(BaseModel):
    email: EmailStr
    password: str

# 토큰 검증
class UserTokenSchema(BaseModel):
    id: int
    email: str
    