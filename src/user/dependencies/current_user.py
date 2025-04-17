from fastapi import Request, HTTPException
from user.schemas.response import UserSchema
import logging

logger = logging.getLogger(__name__)

async def get_current_user(request: Request) -> UserSchema:
    """
    ✅ request.state.session에서 인증된 사용자 정보를 꺼내는 공통 의존성
    - 세션이 없거나 손상되었을 경우 로깅 포함
    """
    session = getattr(request.state, "session", {})
    user_data = session.get("user")

    if not user_data:
        logger.warning("❌ [AUTH] 세션에 사용자 정보 없음 (비로그인 상태)")
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")

    try:
        return UserSchema(**user_data)  # ✅ Pydantic 객체로 변환
    except Exception as e:
        logger.warning(f"❌ [AUTH] 세션 사용자 파싱 실패: {e}")
        raise HTTPException(status_code=401, detail="세션 사용자 정보가 손상되었습니다.")
