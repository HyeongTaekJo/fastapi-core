from fastapi import APIRouter, Depends
from post.schemas.request import CreatePostSchema, UpdatePostSchema, PaginatePostSchema, CreatePostForm
from auth.tokens.access_token import access_token
from post.service import PostService
from post.image.service import PostImageService
from post.image.schemas.request import CreatePostImageSchema
from common.image.model import ImageModelType
from database.session_context import get_db_from_context  # Context에서 세션 꺼내기
from user.dependencies.current_user import get_current_user
from user.dependencies.current_cart import get_current_cart
from user.model import UserModel
from post.file.file_service import PostFileService
from user.dependencies.role_guard import role_guard
from user.const.roles import RolesEnum
from post.dependencies.owner_or_admin import is_post_owner_or_admin

# test

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
    _1: None = Depends(access_token),                # 토큰이 있어야지 접근 가능
    _2: None = Depends(role_guard(RolesEnum.ADMIN)), # user 데이터가 ADMIN인 경우에만 접근 가능(없으면 그냥 다 접근 가능)
    _3: None = Depends(is_post_owner_or_admin),      # 작성자 또는 ADMIN만 접근 가능(모델별로 따로 작성 필요)
    user: UserModel = Depends(get_current_user),     # user 필요시 request.state.user 꺼내쓰거나, 세션(get_current_user)에서 꺼내쓰기
    cart: dict[int, int] = Depends(get_current_cart)  
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

