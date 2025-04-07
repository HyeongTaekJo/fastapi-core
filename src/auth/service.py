import base64
import bcrypt
# from jose import jwt, JWTError  
import jwt  # python-jose 대신 pyjwt 사용
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import HTTPException, Depends,status
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from user.schemas.response import UserSchema
from common.const.settings import settings  # 환경 변수 설정
from auth.schemas.response import TokenSchema
from user.repository import UserRepository
from auth.schemas.request import RegisterUserSchema
from user.model.model import UserModel
from auth.schemas.request import UserTokenSchema
from auth.repository import AuthRepository
from database.redis_connection import redis

class AuthService:
    def __init__(self):
        self.userRepository = UserRepository()
        self.authRepository = AuthRepository()

    # 완료
    def extract_token(self, auth_header: str, is_bearer: bool) -> str:
        """Authorization 헤더에서 토큰을 추출"""
        if not auth_header:
            raise HTTPException(status_code=401, detail="Authorization header에 토큰이 없습니다.")
        
        token_type, token = auth_header.split(" ", 1)
        expected_type = "Bearer" if is_bearer else "Basic"
        
        if token_type != expected_type:
            raise HTTPException(status_code=401, detail="잘못된 토큰입니다.")
        
        return token
    
    async def rotate_token(self, token: str, is_refresh: bool) -> str:
        # 1. 토큰 디코딩
        try:
            decode = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="잘못된 토큰입니다.")

        # 2. 타입 체크
        if decode.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Refresh 토큰만 허용됩니다.")
        
        # 3. 유저 정보 추출
        user_id = decode.get("sub")
        user_email = decode.get("email")

        # 4. Redis에서 저장된 토큰 조회
        saved_token = await self.authRepository.get_refresh_token(user_id)

        if saved_token != token:
            raise HTTPException(status_code=401, detail="유효하지 않은 Refresh Token 입니다.")

        # 5. 새 토큰 발급
        user = UserTokenSchema(id=user_id, email=user_email)
        new_token = self.sign_token(user, is_refresh=True)

        
        # 6. AccessToken만 재발급할 때는 Redis 저장 X
        if is_refresh:
            new_refresh_token = self.sign_token(user, is_refresh=True)
            await self.authRepository.save_refresh_token(user_id, new_refresh_token)
            return new_refresh_token
        else:
            new_access_token = self.sign_token(user, is_refresh=False)
            return new_access_token

    # 완료
    def decode_basic_token(self, token: str) -> dict:
        """Base64로 인코딩된 `email:password`를 디코딩"""
        try:
            decoded_bytes = base64.b64decode(token)
            decoded_str = decoded_bytes.decode("utf-8")
            email, password = decoded_str.split(":")

            return {"email": email, "password": password}  # 딕셔너리 반환
        except Exception:
            raise HTTPException(status_code=401, detail="잘못된 Basic Token 입니다.")

    # 완료
    def verify_token(self, token: str) -> dict:
        """JWT 검증"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="잘못된 토큰입니다.")

    # 완료
    def sign_token(self, user: UserTokenSchema, is_refresh: bool) -> str:
        """JWT 발급"""
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "type": "refresh" if is_refresh else "access",
            "exp": datetime.now() + timedelta(seconds=10800 if is_refresh else 3600)  # 3시간, 1시간
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
        # is_refresh = True (리프레시 토큰) → 3시간 (10800초)
        # is_refresh = False (액세스 토큰) → 1시간 (3600초)

    # 완료
    async def authenticate_with_email_password(self, email: str, password: str) -> UserSchema:
        """이메일과 비밀번호로 사용자 인증"""
        user = await self.userRepository.get_user_by_email(email)

        if not user:
            raise HTTPException(status_code=401, detail="존재하지 않는 User 입니다.")

        if not bcrypt.checkpw(
            password.encode("utf-8"), # byte 타입으로 변환
            user.password.encode("utf-8"),  # 해시된 비밀번호도 bytes로 변환
        ):
            raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")

        return UserSchema.model_validate(user)  # Pydantic Schema 반환
    
    # 완료
    async def login_user(self, user: UserSchema) -> TokenSchema:
        """사용자 로그인 후 토큰 발급 + Redis 저장"""
        access_token = self.sign_token(user, is_refresh=False)
        refresh_token = self.sign_token(user, is_refresh=True)

        # Redis 저장
        await self.authRepository.save_refresh_token(user.id, refresh_token)

        # TokenSchema 객체로 반환
        return TokenSchema(access_token=access_token, refresh_token=refresh_token)


    # 완료
    async def register_user(self, user_data: RegisterUserSchema) -> TokenSchema:
        """회원가입 비즈니스 로직"""
         # 이메일 중복 검사
        existing_user = await self.userRepository.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 등록된 이메일입니다."
            )


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
        new_user = await self.userRepository.create_user(new_user_model)

        # Pydantic DTO 변환
        user_schema = UserSchema.model_validate(new_user)
        return await self.login_user(user_schema)  # 로그인 처리
    
@staticmethod
def decode_jwt_token(token: str) -> UserTokenSchema:
    """JWT 토큰을 검증하고, 사용자 정보(id, email)를 추출"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        return UserTokenSchema(id=payload["sub"], email=payload["email"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="잘못된 토큰입니다.")
