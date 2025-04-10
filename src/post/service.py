from fastapi import HTTPException, status
from post.model import PostModel
from post.schemas.request import CreatePostSchema, UpdatePostSchema, PaginatePostSchema
from post.schemas.response import PostSchema, PaginatedPostSchema
from post.repository import PostRepository
from post.image.service import PostImageService
import os
import logging
from common.const.path_consts import POST_IMAGE_PATH  # 이미지 저장 경로도 import 필요
from common.const.path_consts import FILE_UPLOAD_PATH
from post.file.file_service import PostFileService
from common.file.file_service import FileService

logger = logging.getLogger(__name__)

class PostService:
    def __init__(self):
        self.post_repo = PostRepository()  # repo도 동일 세션을 context에서 사용 트랜잭션을 위해서
        self.post_image_service = PostImageService()
        self.file_service = FileService(FILE_UPLOAD_PATH)

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

    async def update_post_content(self, user_id: int, post_id: int, data: UpdatePostSchema):
        post = await self.post_repo.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="존재하지 않는 게시글입니다.")
        if post.author_id != user_id:
            raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")

        await self.post_repo.update_post(post, data)
    
    async def delete_post(self, post_id: int):
        post = await self.post_repo.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="게시글이 존재하지 않습니다.")

        # ✅ 파일 경로만 미리 수집
        deleted_file_paths = await self.file_service.collect_file_paths("post", post_id)

        # ✅ Post 삭제 → File은 CASCADE로 함께 삭제
        await self.post_repo.delete_post(post_id)

        # ✅ 트랜잭션 성공 이후 디스크에서 파일 제거
        for path in deleted_file_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    logger.warning(f"⚠️ 파일 삭제 실패: {path} - {e}")
       
        
