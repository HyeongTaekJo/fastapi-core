from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator
from typing import Optional
from user.const.roles import RolesEnum 

# 회원가입 요청 스키마
class RegisterUserSchema(BaseModel):
    email: Optional[EmailStr] = None
    login_id: Optional[str] = Field(default=None, min_length=4, max_length=30)
    phone: Optional[str] = Field(default=None, min_length=10, max_length=20)
    nickname: Optional[str] = None
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
    id: int
    email: Optional[EmailStr] = None
    login_id: Optional[str] = None
    phone: Optional[str] = None

    @model_validator(mode="after")
    def exactly_one_identifier(cls, values):
        identifiers = [values.email, values.login_id, values.phone]
        provided = [i for i in identifiers if i is not None]

        if len(provided) != 1:
            raise ValueError("email, login_id, phone 중 정확히 하나만 입력해야 합니다.")
        
        return values

# 공통 필드
class BaseLoginSchema(BaseModel):
    id: int
    nickname: Optional[str] = None
    role: RolesEnum

# 이메일 로그인용
class EmailLoginSchema(BaseLoginSchema):
    email: EmailStr

# 아이디 로그인용
class LoginIdLoginSchema(BaseLoginSchema):
    login_id: str

# 핸드폰 로그인용
class PhoneLoginSchema(BaseLoginSchema):
    phone: str
    