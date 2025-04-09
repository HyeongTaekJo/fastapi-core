from pydantic import BaseModel, Field
from typing import Optional, List
from common.schemas.pagination_request import BasePaginationSchema

class CreatePostSchema(BaseModel):
    title: str
    content: str
    images: Optional[List[str]] = Field(default_factory=list, description="temp 폴더에 저장된 이미지 파일명 리스트")

class UpdatePostSchema(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    images: Optional[List[str]] = None

class PaginatePostSchema(BasePaginationSchema):
    # 아래의 것들을 Query 파라미터로 보내지 않아도 상관없다.
    # 만일, 이 외에 별도로 추가적인 where 조건을 넣고 싶은 경우, service와 Filter Mapper를 수정해야 할 수 있다.
    # 이유는 i_like의 경우 %i_like% 이러한 변형이 필요하기 때문이다.
    where__likeCount__more_than: Optional[int] = Field(default=None, description="좋아요 개수 최소값")
    where__title__i_like: Optional[str] = Field(default=None, description="제목 검색")
    where__id__between: Optional[str] = Field(default=None, description="ID 범위 (예: 10,20)")