from fastapi import Depends, HTTPException, Request
from starlette.status import HTTP_403_FORBIDDEN

from user.const.roles import RolesEnum

def role_guard(required_role: RolesEnum):
    async def guard(request: Request):
        user = getattr(request.state, "user", None)

        # 여기서 user는 access_token에서 미리 세팅된 상태여야 함
        if not user or user.role != required_role:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
    return guard  # ✅ 그냥 guard 함수 자체를 리턴
