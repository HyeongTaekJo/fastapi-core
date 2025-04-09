from typing import List, Optional
from pydantic import BaseModel
from user.schemas.response import UserSchema
from common.image.schemas.response import ImageSchema

class PostSchema(BaseModel):
    id: int
    user: UserSchema   # 프론트엔드 담당자가 user의 id, email만 리턴해달라고 하면 그에 맞는 user스키마 생성
    title: str
    content: str
    likeCount: int
    commentCount: int
    images: List[ImageSchema] = []  # 이미지 리스트 추가

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

###########################################
# 추후에 페이지 네이션을 확장하기 좋음
# 즉, 아래와 같이 response를 정의하는게 좋음
#
# class PaginatedPostListSchema(BaseModel):
#     total_count: int  # 전체 개수
#     current_page: int  # 현재 페이지
#     per_page: int  # 한 페이지당 개수
#     total_pages: int  # 전체 페이지 개수
#     posts: List[PostSchema]  # 실제 데이터 리스트