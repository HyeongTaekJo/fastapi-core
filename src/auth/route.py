from fastapi import APIRouter, Depends, Request, Response, status
from auth.service import AuthService
from user.schemas.response import UserSchema
from auth.tokens.basic_token import basic_token
from auth.schemas.request import RegisterUserSchema
from auth.tokens.refresh_token import refresh_token
from auth.utils.cookies import set_refresh_token_cookie
from fastapi.responses import JSONResponse
from auth.tokens.access_token import access_token
from auth.schemas.request import EmailLoginSchema
from auth.schemas.request import LoginIdLoginSchema
from auth.schemas.request import PhoneLoginSchema
from common.utils.tx_debugger import log_tx_state
from database.session_context import get_db_from_context

router = APIRouter(prefix="/auth", tags=["auth"])

# 로그인
@router.post("/login/email")
async def post_login_email(
    # 특정 API에만 적용
    # BasicToken 함수를 수행하면 인증된 user  객체가 반환된다.
    # 로그인을 수행하면 accessToken, refreshToken이 반환되기 때문에
    # 클라이언트에서 accessToken을 가지고 요청을 보내면 API들이 작동된다.
    # 단, Depends(AccessToken)를 통해서 로그인한 사용자만 접근 가능한 API로 설정한 경우 accessToken이 필요하다.
    # 참고 -> Depends(AccessToken)를 수행하면 요청(req)에 user를 들고 있는데 이것을 Depends(User)를 통해서 req.user을 빼와서 바로 user를 사용할 수 있다.
    request : Request,
    response: Response,
    # 로그인 API - Basic Token 인증
    _1: None = Depends(basic_token),
    auth_service: AuthService = Depends(),
    
):
    user : UserSchema = request.state.user

     # EmailLoginSchema로 명시적 변환
    login_user = EmailLoginSchema.model_validate(user.model_dump())

    tokens = await auth_service.login_user(request, login_user)

    # refresh_token을 쿠키에 저장
    set_refresh_token_cookie(response, tokens.refresh_token)

    # refresh 토큰은 보안상 쿠키 security에 보관하고 따로 보내주지 않는다.
    # 단, frontend 담당자가 refresh_token을 쿠키에서 꺼내서 사용하면 된다고 알려줘야 한다.
    return {"access_token": tokens.access_token}


# 로그아웃
@router.post("/logout")
async def logout(
    request: Request,
    _: None = Depends(access_token),
    auth_service: AuthService = Depends(),
):
    access_token = request.state.token  # access_token은 미리 검증된 상태
    await auth_service.logout(request, access_token)

    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": "로그아웃이 완료되었습니다."}
    )
    response.delete_cookie("refresh_token")
    return response


# 회원가입(email 방식)
@router.post("/register/email")
async def register_user(
    request: Request,
    user_data: RegisterUserSchema,
    response: Response,
    auth_service: AuthService = Depends()
):
    session = get_db_from_context()

    # 회원가입만 트랜잭션으로 처리
    async with session.begin():
        new_user = await auth_service.register_user(request, user_data)  # 회원가입만 수행

    # 별도의 트랜잭션으로 login_user 호출
    tokens = await auth_service.login_user(request, new_user)

    # 쿠키 설정 및 반환
    set_refresh_token_cookie(response, tokens.refresh_token)
    return {"access_token": tokens.access_token}

# access_token 재발급
@router.post("/token/access")
async def new_access_token(
        request: Request,
        _: refresh_token = Depends(),  # Refresh Token 검증
        auth_service: AuthService = Depends(AuthService)
    ):
    # Refresh Token 추출
    raw_token = request.state.token

    # 새로운 Access Token 발급
    new_token = await auth_service.rotate_token(raw_token, is_refresh=False)

    return {"access_token": new_token}

# refresh_token 재발급
@router.post("/token/refresh")
async def new_refresh_token(
        request: Request,
        response: Response,
        _: refresh_token = Depends(),  # Refresh Token 검증
        auth_service: AuthService = Depends(AuthService)
    ):
    # Refresh Token 추출
    raw_token = request.state.token

    # 새로운 refresh Token 발급
    new_token = await auth_service.rotate_token(raw_token, is_refresh=True)

    # refresh_token을 쿠키에 저장
    res = JSONResponse(
        status_code=200,
        content={"detail": "Refresh token updated successfully"}
    )

    set_refresh_token_cookie(res, new_token)  
    
    return res

# 로그인(id 방식)
@router.post("/login/login_id")
async def login_login_id(
    request : Request,
    response: Response,
    _1: None = Depends(basic_token),  # login_id 기반 BasicAuth
    auth_service: AuthService = Depends(),
):
    user : UserSchema = request.state.user

    # LoginIdLoginSchema로 명시적 변환
    login_user = LoginIdLoginSchema.model_validate(user.model_dump())

    tokens = await auth_service.login_user(request,login_user)
    set_refresh_token_cookie(response, tokens.refresh_token)
    return {"access_token": tokens.access_token}

# 로그인(핸드폰 방식)
@router.post("/login/phone")
async def login_phone(
    request : Request,
    response: Response,
    _1: None = Depends(basic_token),  # phone 기반 BasicAuth
    auth_service: AuthService = Depends(),
):
    user : UserSchema = request.state.user
    
    # PhoneLoginSchema로 명시적 변환
    login_user = PhoneLoginSchema.model_validate(user.model_dump())

    tokens = await auth_service.login_user(request,login_user)
    set_refresh_token_cookie(response, tokens.refresh_token)
    return {"access_token": tokens.access_token}


# 회원가입(id 방식)
@router.post("/register/login_id")
async def register_user_login_id(
    request: Request,
    user_data: RegisterUserSchema,
    response: Response,
    auth_service: AuthService = Depends()
):
    session = get_db_from_context()

    # 회원가입만 트랜잭션으로 수행
    async with session.begin():
        user_schema = await auth_service.register_user(request, user_data)

    # 로그인 수행 (별도 트랜잭션으로)
    tokens = await auth_service.login_user(request, user_schema)

    set_refresh_token_cookie(response, tokens.refresh_token)
    return {"access_token": tokens.access_token}

# 회원가입(핸드폰 방식)
@router.post("/register/phone")
async def register_user_phone(
    request: Request,
    user_data: RegisterUserSchema,
    response: Response,
    auth_service: AuthService = Depends()
):
    session = get_db_from_context()

    # 회원가입만 트랜잭션으로 수행
    async with session.begin():
        user_schema = await auth_service.register_user(request, user_data)

    # 로그인 수행 (별도 트랜잭션으로)
    tokens = await auth_service.login_user(request, user_schema)

    set_refresh_token_cookie(response, tokens.refresh_token)
    return {"access_token": tokens.access_token}
