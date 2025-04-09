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
        # 미들웨어에서 설정한 Context 기반 세션을 사용
        self.session = get_db_from_context()
        self.common_service = CommonService()

    async def get_posts(self) -> List[PostModel]:
        result = await self.session.scalars(select(PostModel))
        return list(result)

    async def get_posts_paginated(self, request: PaginatePostSchema):
        # 조인이 필요한 경우
        # 단, 모델간의 관계가 lazy="selectin" 인 경우는 필요없음
        # 단, lazy="raise" 인 경우는 반드시 selectinload로 관계설정으로 select 해오는게 필요함
        #     그러므로  lazy="raise"면 query를 같이 보내야 한다.
        query = get_default_post_query()

        return await self.common_service.paginate(
            request,
            PostModel,
            self.session,
            base_query=None,  # 또는 query,
            path="posts"
        )

    async def get_post_by_id(self, id: int) -> PostModel | None:
        stmt = get_default_post_query().where(PostModel.id == id)
        return await self.session.scalar(stmt)

    async def create_post(self, author_id: int, request: CreatePostSchema) -> PostModel:
        post = PostModel(
            title=request.title,
            content=request.content,
            author_id=author_id,  #  기본값 설정
            likeCount=0,  #  기본값 설정
            commentCount=0  #  기본값 설정
        )

        self.session.add(post)  # session object에 추가
        await self.session.flush()  # ID 가져오기 위해 refresh 대신 flush 사용 가능
        await self.session.refresh(post)  # 데이터베이스에서 다시 읽어옴 -> todo_id까지 포함된 것을 가져옴
        return post

    async def update_post(self, post: PostModel, data: UpdatePostSchema):
        if data.title is not None:
            post.title = data.title
        if data.content is not None:
            post.content = data.content
        await self.session.flush()



    async def delete_post(self, id: int) -> None:
        # 기존 post 찾기
        existing_post = await self.get_post_by_id(id)

        if not existing_post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="존재하지 않는 post 입니다.")

        await self.session.execute(delete(PostModel).where(PostModel.id == id))
        # await self.session.commit() # ❌ commit()은 생략! (라우터에서 begin() 블록이 처리)

    async def generate_posts(self):
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
        await self.session.execute(insert(PostModel).values(posts))
        await self.session.commit()
