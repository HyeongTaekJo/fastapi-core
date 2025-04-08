from pydantic import BaseModel, EmailStr
from typing import List
from user.const.roles import RolesEnum
from typing import Optional

class UserSchema(BaseModel):
   
    id: int
    nickname: str
    email: Optional[EmailStr] = None
    login_id: Optional[str] = None
    phone: Optional[str] = None
    role: RolesEnum
    # password: str


    # pydantic에서 SQLAlchemy를 바로 읽을 수 있도록 하는 것
    # FastAPI에서 SQLAlchemy ORM 모델을 직접 응답으로 반환하면, 기본적으로 JSON 변환이 불가능함.
    # FastAPI에서 orm_mode = True를 사용하면, SQLAlchemy ORM 객체를 Pydantic Schema로 쉽게 변환하여 API 응답으로 보낼 수 있습니다.
    # 즉, pydantic은 fastapi가 자동으로 json으로 변환해준다.
    class Config:
        from_attributes = True  # Pydantic v2에서는 필수

class UserListSchema(BaseModel):
    users: List[UserSchema]

# 만일 추가로 user 테이블에서 컬럼의 값을 가져오고 싶은 경우
# UserSchema를 상속하고 추가로 가져오고 싶은 컬럼을 추가하면 된다.
class DetailedUserSchema(UserSchema):
    nickname: str
    password: str  # 보통 응답엔 안 넣지만 예시로