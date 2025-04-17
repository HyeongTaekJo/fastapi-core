import base64
import bcrypt
# from jose import jwt, JWTError  
import jwt  # python-jose 대신 pyjwt 사용
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import HTTPException, Depends, status, Request
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from user.schemas.response import UserSchema
from common.const.settings import settings  # 환경 변수 설정
from auth.schemas.response import TokenSchema
from user.repository import UserRepository
from auth.schemas.request import RegisterUserSchema
from user.model import UserModel
from auth.repository import AuthRepository
from cache.redis_connection import redis
from auth.const.fields import UNIQUE_USER_FIELDS
from common.exceptions.base import ConflictException
from common.exceptions.base import UnauthorizedException
from common.exceptions.base import NotFoundException  # 추가됨
from auth.schemas.request import LoginUserSchema
from cache.redis_context import get_redis_from_context
from auth.repository import AuthRepository
from cart.repository import CartRepository


class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.auth_repository = AuthRepository()
        self.cart_repository = CartRepository()

    def extract_token(self, auth_header: str, is_bearer: bool) -> str:
        """Authorization 헤더에서 토큰을 추출"""
        if not auth_header:
            raise UnauthorizedException("Authorization header에 토큰이 없습니다.")
        
        token_type, token = auth_header.split(" ", 1)
        expected_type = "Bearer" if is_bearer else "Basic"
        
        if token_type != expected_type:
            raise UnauthorizedException("잘못된 토큰입니다.")
        
        return token
    
    async def rotate_token(self, token: str, is_refresh: bool) -> str:
        # 1. 토큰 디코딩
        try:
            decode = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("토큰이 만료되었습니다.")
        except jwt.InvalidTokenError:
            raise UnauthorizedException("잘못된 토큰입니다.")

        # 2. 타입 체크
        if decode.get("type") != "refresh":
            raise UnauthorizedException("Refresh 토큰만 허용됩니다.")

        # 3. 유저 정보 추출
        user_id = decode.get("sub")

        # identifier (email, login_id, phone 중 하나)
        identifier_keys = ["email", "login_id", "phone"]
        identifier_data = {k: decode.get(k) for k in identifier_keys if decode.get(k) is not None}

        if not identifier_data or len(identifier_data) != 1:
            raise UnauthorizedException("유효하지 않은 사용자 식별자입니다.")

        # 4. Redis에서 저장된 토큰 조회
        saved_token = await self.auth_repository.get_refresh_token(user_id)
        if saved_token != token:
            raise UnauthorizedException("유효하지 않은 Refresh Token 입니다.")

        # 5. 새로운 토큰 발급을 위한 사용자 객체 구성
        user = LoginUserSchema(id=user_id, **identifier_data)

        # 6. AccessToken만 재발급할 때는 Redis 저장 X
        if is_refresh:
            new_refresh_token = self.sign_token(user, is_refresh=True)
            await self.auth_repository.save_refresh_token(user_id, new_refresh_token)
            return new_refresh_token
        else:
            new_access_token = self.sign_token(user, is_refresh=False)
            return new_access_token

    def decode_basic_token(self, token: str) -> dict:
        """Base64로 인코딩된 `email:password`를 디코딩"""
        try:
            decoded_bytes = base64.b64decode(token)
            decoded_str = decoded_bytes.decode("utf-8")
            email, password = decoded_str.split(":")

            return {"email": email, "password": password}  # 딕셔너리 반환
        except Exception:
            raise UnauthorizedException("잘못된 Basic Token 입니다.")

    def verify_token(self, token: str) -> dict:
        """JWT 검증"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("토큰이 만료되었습니다.")
        except jwt.InvalidTokenError:
            raise UnauthorizedException("잘못된 토큰입니다.")

    def sign_token(self, user: LoginUserSchema, is_refresh: bool) -> str:
        """JWT 발급"""
        identifier_key = None
        identifier_value = None

        for key in ["email", "login_id", "phone"]:
            value = getattr(user, key, None)
            if value is not None:
                identifier_key = key
                identifier_value = value
                break

        if identifier_key is None:
            raise ValueError("유저 식별자가 없습니다.")

        payload = {
            "sub": str(user.id),
            identifier_key: identifier_value,
            "type": "refresh" if is_refresh else "access",
            "exp": datetime.now() + timedelta(seconds=10800 if is_refresh else 3600)
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
        # is_refresh = True (리프레시 토큰) → 3시간 (10800초)
        # is_refresh = False (액세스 토큰) → 1시간 (3600초)

    async def authenticate_with_field(
        self, field: str, identifier: str, password: str
    ) -> UserSchema:
        """필드 기반 사용자 인증"""
        user = await self.user_repository.get_user_by_field(field, identifier)

        if not user:
            raise NotFoundException("User")

        if not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
            raise UnauthorizedException("비밀번호가 일치하지 않습니다.")

        return UserSchema.model_validate(user)
    
    async def login_user(
                self,
                request: Request,
                user: UserSchema) -> TokenSchema:
        """사용자 로그인 후 토큰 발급 + Redis 저장"""
        access_token = self.sign_token(user, is_refresh=False)
        refresh_token = self.sign_token(user, is_refresh=True)

        # Redis 저장
        await self.auth_repository.save_refresh_token(user.id, refresh_token)

        ###########################################################################

        # 🧠 Redis 세션에 있는 장바구니와 DB 장바구니 병합
        redis_cart = request.state.session.get("cart", {})
        db_cart = await self.cart_repository.get_user_cart_dict(user.id)

        merged_cart = db_cart.copy()
        for pid, qty in redis_cart.items():
            merged_cart[pid] = merged_cart.get(pid, 0) + qty

        # 💾 병합 후 MySQL 저장
        await self.cart_repository.save_user_cart(user.id, merged_cart)

        ###########################################################################

        # ✅ Redis 세션 갱신
        session = request.state.session
        session["user"] = { "id": user.id, "email": user.email }
        session["cart"] = merged_cart

        ###########################################################################

        # TokenSchema 객체로 반환
        return TokenSchema(access_token=access_token, refresh_token=refresh_token)


    async def register_user(
            self,
            request: Request,
            user_data: RegisterUserSchema) -> TokenSchema:
        """회원가입 비즈니스 로직"""
        
        for field in UNIQUE_USER_FIELDS:
            value = getattr(user_data, field, None)
            if value and await self.user_repository.get_user_by_field(field, value):
                raise ConflictException(f"이미 등록된 {field}입니다.")

        # 환경 변수에서 BCRYPT_ROUNDS 값 가져오기
        rounds = settings.BCRYPT_ROUNDS  
        
        # 비밀번호 해싱은 서비스에서 처리
        hashed_password = bcrypt.hashpw(
            user_data.password.encode("utf-8"), 
            bcrypt.gensalt(rounds=rounds)
        ).decode("utf-8")


        # Pydantic -> SQLAlchemy 변환 (UserModel.create() 사용)
        new_user_model = UserModel.create(user_data)  # RegisterUserSchema -> UserModel 변환
        new_user_model.password = hashed_password  # 해싱된 비밀번호 적용

        # 레포지토리에 저장
        new_user = await self.user_repository.create_user(new_user_model)

        # Pydantic DTO 변환
        user_schema = UserSchema.model_validate(new_user)
        return await self.login_user(request, user_schema)  # 로그인 처리
    
    async def logout(self, access_token: str):
        payload = self.verify_token(access_token)
        user_id = payload["sub"]
        exp = payload["exp"]

        # 1. access token 블랙리스트 등록
        await self.auth_repository.blacklist_token(access_token, exp)

        # 2. redis에 저장된 refresh token 제거
        await self.auth_repository.delete_refresh_token(user_id)

        # 3. ✅ Redis에 캐시된 user 정보 삭제
        redis = get_redis_from_context()
        redis_key = f"user:{user_id}"
        await redis.delete(redis_key)

@staticmethod
def decode_jwt_token(token: str) -> LoginUserSchema:
    """JWT 토큰을 검증하고, 사용자 정보(id, email)를 추출"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        
        return LoginUserSchema(
            id=int(payload["sub"]),
            email=payload.get("email"),
            login_id=payload.get("login_id"),
            phone=payload.get("phone")
        )
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("토큰이 만료되었습니다.")
    except jwt.InvalidTokenError:
        raise UnauthorizedException("유효하지 않은 토큰입니다.")
