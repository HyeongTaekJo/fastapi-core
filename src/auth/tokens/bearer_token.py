from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.service import AuthService
from user.repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from auth.repository import AuthRepository

security = HTTPBearer()  # Bearer Token 인증 스키마

async def bearer_token(
    request: Request,
    auth_header: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(),
    auth_repository: AuthRepository = Depends(),
    user_repository: UserRepository = Depends()
):
    """
    공통적으로 Bearer Token을 검증하는 Dependency
    """

    # 1. Authorization 헤더가 있는지 확인
    if not auth_header:
        raise HTTPException(status_code=401, detail="토큰이 없습니다.")

    raw_token = auth_header.credentials  # Bearer 토큰 값 추출

    # 2. 블랙리스트 체크 먼저
    if await auth_repository.is_blacklisted(raw_token):
        raise HTTPException(status_code=401, detail="로그아웃된 토큰입니다.")

    # 3. 토큰 검증 (유효성 검사 및 페이로드 추출)
    payload = auth_service.verify_token(raw_token)

    # 4. 사용자 정보 조회
    # 유연한 방식 (선택사항)
    identifier = (
        payload.get("email") or 
        payload.get("login_id") or 
        payload.get("phone")
    )

    if not identifier:
        raise HTTPException(status_code=401, detail="토큰에 사용자 식별 정보가 없습니다.")
    
    # 인증 끝났으므로 트랜잭션 종료
    # commit or rollback 중 선택 (쓰기 없음 → rollback도 괜찮음)
    # 이게 없으면 router에서 async with session.begin(): 이것으로 트랜잭션할 때 오류남
    db: AsyncSession = user_repository.session
    await db.rollback()

    # 5. 요청 객체에 사용자 및 토큰 정보 추가
    request.state.user_id = payload["sub"]  # user_id만 저장
    request.state.token = raw_token
    request.state.token_type = payload.get("type", "unknown")  # access 또는 refresh

    """
    Depends(AccessTokenDepency)를 통과한 api에는 request에 user가 있기 때문에
    return 을 안해도 된다.
    """
    # return user  # 최종적으로 인증된 사용자 반환
