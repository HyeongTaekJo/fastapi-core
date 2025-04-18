# user/dependencies/optional_user.py
from fastapi import Request
from typing import Optional
from user.schemas.response import UserSchema

async def get_optional_user(request: Request) -> Optional[UserSchema]:
    session = getattr(request.state, "session", {})
    user_data = session.get("user")

    if not user_data:
        return None  # ❗️로그인 안 돼도 그냥 None 반환

    try:
        return UserSchema(**user_data)
    except Exception:
        return None  # ❗️파싱 실패해도 None 처리
