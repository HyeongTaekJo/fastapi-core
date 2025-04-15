from fastapi import Request, HTTPException, Depends
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST
from post.repository import PostRepository
from user.schemas.response import UserSchema
from user.const.roles import RolesEnum


async def is_post_owner_or_admin(request: Request):

    post_repo = PostRepository()  # 전역 생성
    """
    게시글 작성자이거나 관리자일 경우만 통과 가능한 Guard
    """
    user: UserSchema = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="로그인이 필요합니다.")

    if user.role == RolesEnum.ADMIN:
        return

    post_id = request.path_params.get("id") or request.path_params.get("post_id")
    if not post_id:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="post_id가 필요합니다.")

    post = await post_repo.get_post_by_id(int(post_id))
    if not post or not post.user or post.user.id != user.id:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="작성자 본인만 접근할 수 없습니다.")
