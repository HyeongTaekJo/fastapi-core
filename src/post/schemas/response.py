from typing import List, Optional
from pydantic import BaseModel
from user.schemas.response import UserSchema
from common.file.schemas.response import FileSchema

class PostSchema(BaseModel):
    id: int
    user: UserSchema   # 프론트엔드 담당자가 user의 id, email만 리턴해달라고 하면 그에 맞는 user스키마 생성
    title: str
    content: str
    likeCount: int
    commentCount: int
    files: List[FileSchema] = []   

    # pydantic에서 SQLAlchemy를 바로 읽을 수 있도록 하는 것
    # FastAPI에서 SQLAlchemy ORM 모델을 직접 응답으로 반환하면, 기본적으로 JSON 변환이 불가능함.
    # FastAPI에서 orm_mode = True를 사용하면, SQLAlchemy ORM 객체를 Pydantic Schema로 쉽게 변환하여 API 응답으로 보낼 수 있습니다.
    # 즉, pydantic은 fastapi가 자동으로 json으로 변환해준다.
    class Config:
        from_attributes = True  # Pydantic v2에서는 필수

class PostListSchema(BaseModel):
    posts: List[PostSchema]


class PaginatedPostSchema(BaseModel):
    posts: List[PostSchema]
    total: Optional[int] = None
    count: Optional[int] = None
    cursor: Optional[dict] = None
    next: Optional[str] = None

