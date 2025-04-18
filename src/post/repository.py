from sqlalchemy import select, delete, insert
from fastapi import HTTPException, status
from post.model import PostModel
from post.schemas.request import PaginatePostSchema, CreatePostSchema
from common.pagination.service import CommonService
from post.query.default_options import get_default_post_query
from typing import List
from database.session_context import get_db_from_context
from post.schemas.request import UpdatePostSchema

# 비동기 engine을 사용하므로 repository는 비동기로 실행 해야한다.
class PostRepository:
    def __init__(self):
        self.common_service = CommonService()

    async def get_posts(self) -> List[PostModel]:
        session = get_db_from_context()
        result = await session.scalars(select(PostModel))
        return list(result)

    async def get_posts_paginated(self, request: PaginatePostSchema):
        session = get_db_from_context()

        # 조인이 필요한 경우
        # 단, 모델간의 관계가 lazy="selectin" 인 경우는 필요없음
        # 단, lazy="raise" 인 경우는 반드시 selectinload로 관계설정으로 select 해오는게 필요함
        #     그러므로  lazy="raise"면 query를 같이 보내야 한다.
        query = get_default_post_query()

        return await self.common_service.paginate(
            request,
            PostModel,
            session,
            base_query=None,  # 또는 query,
            path="posts"
        )

    async def get_post_by_id(self, id: int) -> PostModel | None:
        session = get_db_from_context()
        stmt = get_default_post_query().where(PostModel.id == id)
        return await session.scalar(stmt)

    async def create_post(self, author_id: int, request: CreatePostSchema) -> PostModel:
        session = get_db_from_context()

        post = PostModel(
            title=request.title,
            content=request.content,
            author_id=author_id,  #  기본값 설정
            likeCount=0,  #  기본값 설정
            commentCount=0  #  기본값 설정
        )

        session.add(post)
        await session.flush()

        # 관계 포함된 post를 다시 SELECT해서 리턴
        # 트랜잭션시, refresh 지양할 것(오류남)
        return await self.get_post_by_id(post.id)

    async def update_post(self, post: PostModel, data: UpdatePostSchema):
        session = get_db_from_context()

        if data.title is not None:
            post.title = data.title
        if data.content is not None:
            post.content = data.content
        await session.flush()

    async def delete_post(self, id: int) -> None:
        session = get_db_from_context()

        # 기존 post 찾기
        existing_post = await self.get_post_by_id(id)

        if not existing_post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="존재하지 않는 post 입니다.")

        await session.execute(delete(PostModel).where(PostModel.id == id))
        # await session.commit() # ❌ commit()은 생략! (라우터에서 begin() 블록이 처리)

    async def generate_posts(self):
        session = get_db_from_context()

        """ 특정 유저의 더미 포스트 100개 생성 """
        posts = [
            {
                "author_id": 1,  # user_id 1로 설정
                "title": f"임의로 생성된 포스트 {i}",
                "content": f"임의로 생성된 포스트 {i}의 내용",
                "likeCount": 0,
                "commentCount": 0
            }
            for i in range(100)
        ]

        # SQLAlchemy의 `insert`를 사용하여 100개 일괄 삽입 (Batch Insert)
        await session.execute(insert(PostModel).values(posts))
        await session.commit()
