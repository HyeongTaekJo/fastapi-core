from fastapi import HTTPException, status
from post.model.model import PostModel
from post.schemas.request import CreatePostSchema, UpdatePostSchema, PaginatePostSchema
from post.schemas.response import PostSchema, PaginatedPostSchema
from post.repository import PostRepository

class PostService:
    def __init__(self):
        self.post_repo = PostRepository()  # repo도 동일 세션을 context에서 사용 트랜잭션을 위해서

    async def generate_dummy_posts(self):
        await self.post_repo.generate_posts()
        return True

    async def get_paginated_posts(self, request: PaginatePostSchema):
        result = await self.post_repo.get_posts_paginated(request)

        response = PaginatedPostSchema(
            #  model_validate(검증함) VS model_construct(검증 안함)
            posts=[PostSchema.model_validate(post) for post in result.data],
            total=getattr(result, "total", None),
            count=getattr(result, "count", None),
            cursor=getattr(result, "cursor", None),
            next=getattr(result, "next", None),
        )

        return response.model_dump(exclude_none=True)  # null 값은 제거된 상태로 응답됨 

    async def get_post_by_id(self, post_id: int):
        post = await self.post_repo.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")

        # Pydantic 모델로 만들어서 리턴(검증, json으로 변환 해줌)
        return PostSchema.model_validate(post)

    async def create_post(self, author_id: int, data: CreatePostSchema):
        # Pydantic 모델(CreateToDoReqeust)로 받은 것을 SQLAlchemy ORM 객체로 변환 -> 이렇게 해야지 DB에 들어감
        post = PostModel.create(request=data)

        # SQLAlchemy ORM 객체로 변환된 것을 가지고 DB에 저장
        saved = await self.post_repo.create_post(author_id, post)

        # Pydantic 모델로 만들어서 리턴(검증, json으로 변환 해줌)
        return PostSchema.model_validate(saved)

    async def update_post(self, post_id: int, data: UpdatePostSchema):
        # Pydantic 모델(CreateToDoReqeust)로 받은 것을 SQLAlchemy ORM 객체로 변환 -> 이렇게 해야지 DB에 들어감
        updated = PostModel.update(request=data)

        # SQLAlchemy ORM 객체로 변환된 것을 가지고 DB에 저장
        post = await self.post_repo.update_post(post_id, updated)

        # Pydantic 모델로 만들어서 리턴(검증, json으로 변환 해줌)
        return PostSchema.model_validate(post)

    async def delete_post(self, post_id: int):
        await self.post_repo.delete_post(post_id)
