from fastapi import APIRouter, Depends, Request, Response
from auth.service import AuthService
from user.schemas.response import UserSchema
from auth.tokens.basic_token import basic_token
from auth.schemas.request import RegisterUserSchema
from auth.tokens.refresh_token import refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login/email")
async def post_login_email(
    # 특정 API에만 적용
    # BasicToken 함수를 수행하면 인증된 user  객체가 반환된다.
    # 로그인을 수행하면 accessToken, refreshToken이 반환되기 때문에
    # 클라이언트에서 accessToken을 가지고 요청을 보내면 API들이 작동된다.
    # 단, Depends(AccessToken)를 통해서 로그인한 사용자만 접근 가능한 API로 설정한 경우 accessToken이 필요하다.
    # 참고 -> Depends(AccessToken)를 수행하면 요청(req)에 user를 들고 있는데 이것을 Depends(User)를 통해서 req.user을 빼와서 바로 user를 사용할 수 있다.
    
    response: Response,
    # 로그인 API - Basic Token 인증
    user: UserSchema = Depends(basic_token),
    auth_service: AuthService = Depends(),
    
):
    access_token, refresh_token = await auth_service.login_user(user)

    # 쿠키 저장
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=60 * 60 * 24 * 7,
        samesite="lax",
        secure=True
    )

    # refresh 토큰은 보안상 쿠키 security에 보관하고 따로 보내주지 않는다.
    # 단, frontend 담당자가 refresh_token을 쿠키에서 꺼내서 사용하면 된다고 알려줘야 한다.
    return {"access_token": access_token}

@router.post("/register/email")
async def register_user(
        request: RegisterUserSchema,
        auth_service: AuthService = Depends(AuthService)
    ):
    return await auth_service.register_user(request)

# access_token 재발급
@router.post("/token/access")
def new_access_token(
        request: Request,
        _: refresh_token = Depends(),  # Refresh Token 검증
        auth_service: AuthService = Depends(AuthService)
    ):
    # Refresh Token 추출
    raw_token = request.state.token

    # 새로운 Access Token 발급
    new_token = auth_service.rotate_token(raw_token, is_refresh_token=False)

    return {"access_token": new_token}

# refresh_token 재발급
@router.post("/token/refresh")
def new_refresh_token(
        request: Request,
        _: refresh_token = Depends(),  # Refresh Token 검증
        auth_service: AuthService = Depends(AuthService)
    ):
    # Refresh Token 추출
    raw_token = request.state.token

    # 새로운 refresh Token 발급
    new_token = auth_service.rotate_token(raw_token, is_refresh_token=True)

    return {"refresh_token": new_token}