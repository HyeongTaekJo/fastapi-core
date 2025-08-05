from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.service import AuthService
from user.repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from auth.repository import AuthRepository
from user.schemas.response import UserSchema
from database.dependencies import get_db
from cache.dependencies import get_redis
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()  # Bearer Token 인증 스키마

async def bearer_token(
    request: Request,
    auth_header: HTTPAuthorizationCredentials = Depends(security),  #  자동으로 Authorization 헤더 파싱
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """
     공통 인증 처리 (Bearer 토큰 검증 + 사용자 정보 로딩 + request.state 주입)
    - 블랙리스트 확인
    - JWT 토큰 검증
    - Redis 세션 기반 사용자 정보 복원 or DB 조회
    - request.state에 user, token, token_type 저장
    """

    auth_service = AuthService(db, redis)                          #  JWT 검증 로직을 담당하는 서비스
    auth_repository = AuthRepository(redis)                    #  토큰 블랙리스트 조회용 Redis 또는 DB
    user_repository = UserRepository(db)                    #  사용자 정보 DB 조회용 Repository

    # 1. Authorization 헤더 확인
    if not auth_header:
        raise HTTPException(status_code=401, detail="토큰이 없습니다.")

    raw_token = auth_header.credentials  # "Bearer xxxxx" → "xxxxx"

    # 2. 로그아웃(블랙리스트) 토큰인지 확인
    if await auth_repository.is_blacklisted(raw_token):
        raise HTTPException(status_code=401, detail="로그아웃된 토큰입니다.")

    # 3. JWT 토큰 유효성 검증 및 payload 파싱
    payload = auth_service.verify_token(raw_token)  # 실패 시 예외 발생

    # 4. payload 내 사용자 ID 추출 (user_id는 sub 필드에 저장됨)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="토큰에 사용자 ID가 없습니다.")

    # 5. 세션에서 사용자 정보 조회
    session = request.state.session
    user_dict = session.get("user")

    user_data = None
    if user_dict:
        try:
            user_data = UserSchema(**user_dict)  #  Pydantic 기반 객체 복원
        except Exception as e:
            logger.warning(f"세션 사용자 정보 파싱 실패: {e}")

    # 6. 세션에 없으면 DB에서 조회 후 세션에 저장
    if not user_data:
        user_model = await user_repository.get_user_by_id(user_id)
        if not user_model:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        user_data = UserSchema.model_validate(user_model)  # SQLAlchemy → Pydantic 변환
        try:
            session["user"] = user_data.model_dump()  #  Redis 세션 갱신
        except Exception as e:
            logger.warning(f"세션 사용자 정보 Redis 저장 실패: {e}")

    # 7. DB 트랜잭션을 명시적으로 종료 (쓰기 작업 없으므로 rollback 안전)
    await db.rollback()

    # 8. request.state에 인증된 유저 및 토큰 정보 저장 (모든 API에서 공유 가능)
    request.state.user = user_data  # 이후 Depends(get_current_user)에서 그대로 사용
    request.state.token = raw_token
    request.state.token_type = payload.get("type", "unknown")  # access / refresh 구분

    """
    Depends(AccessTokenDepency)를 통과한 api에는 request에 user가 있기 때문에
    return 을 안해도 된다.
    """
    # return user  # 최종적으로 인증된 사용자 반환
