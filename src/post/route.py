from fastapi import APIRouter, Depends
from post.schemas.request import CreatePostSchema, UpdatePostSchema, PaginatePostSchema
from auth.tokens.access_token import access_token
from post.service import PostService
from post.image.service import PostImageService
from post.image.schemas.request import CreatePostImageSchema
from common.image.model import ImageModelType
from database.session_context import get_db_from_context  # Context에서 세션 꺼내기
from auth.dependencies.current_user import get_current_user
from user.model import UserModel
from post.file.file_service import PostFileService
from post.form_schemas.create_schema import CreatePostForm

# router 생성
router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/random")
async def generate_dummy_posts(
    _: None = Depends(access_token), # 토큰이 있는 사람만 접근 가능
):
    service = PostService()
    return await service.generate_dummy_posts()


@router.get("")
async def get_paginated_posts(
    request: PaginatePostSchema = Depends(),
    # _: None = Depends(AccessTokenDependency),
):
    service = PostService()
    return await service.get_paginated_posts(request)


@router.get("/{id}")
async def get_post_by_id(
    id: int,
    _: None = Depends(access_token),
    # user: UserModel = Depends(get_current_user) # user 필요시(accessToken이 선행되어야 한다.)
):
    service = PostService()
    return await service.get_post_by_id(id)


@router.post("")
async def create_post(
    request: CreatePostSchema,
    _: None = Depends(access_token),
    user: UserModel = Depends(get_current_user),
):
    session = get_db_from_context()
    post_service = PostService()

    async with session.begin():
        post_id = await post_service.create_post_with_schema(user.id, request)

    return await post_service.get_post_by_id(post_id)  # 트랜잭션 밖에서 안전하게 조회


@router.post("/form")
async def create_post_form(
    form: CreatePostForm = Depends(),
    _: None = Depends(access_token),
    user: UserModel = Depends(get_current_user),
):
    session = get_db_from_context()
    post_service = PostService()

    async with session.begin():
        post_id = await post_service.create_post_with_form(
            user_id=user.id,
            title=form.title,
            content=form.content,
            files=form.files,
        )

    return await post_service.get_post_by_id(post_id)  # 트랜잭션 밖 조회


@router.patch("/{id}")
async def update_post(
    id: int,
    request: UpdatePostSchema,
    _: None = Depends(access_token),
    user: UserModel = Depends(get_current_user),
):
    session = get_db_from_context()
    post_service = PostService()

    async with session.begin():
        post_id = await post_service.update_post_with_schema(user.id, id, request)

    return await post_service.get_post_by_id(post_id)  # 최신 상태 반환


@router.delete("/{id}")
async def delete_post(
    id: int,
    _: None = Depends(access_token),
):
    session = get_db_from_context()

    async with session.begin():
        post_service = PostService()
        await post_service.delete_post(id)
    return {"message": "삭제되었습니다"}

