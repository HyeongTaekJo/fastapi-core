from pydantic_settings import BaseSettings
from pydantic import Field
from common.const.logging_consts import LogLevelEnum


class Settings(BaseSettings):
    # JWT 및 암호화 설정
    JWT_SECRET: str
    HASH_ROUND: int
    ALGORITHM: str
    BCRYPT_ROUNDS: int

    # 서버 설정
    PROTOCOL: str
    HOST: str
    PORT: int

    # 데이터베이스 설정
    DATABASE_CONN: str
    UPLOAD_DIR: str
    SECRET_KEY: str

    # 데이터베이스 개별 설정 (MySQL)
    DB_HOST: str
    DB_PORT: int
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_DATABASE: str

    # Redis 설정
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str | None = None

    # 로그 레벨 - Enum 타입으로 변경
    LOG_LEVEL: LogLevelEnum = Field(
        default=LogLevelEnum.INFO,
        description="로그 레벨 설정 (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    # CORS (Cross-Origin Resource Sharing)
    ALLOWED_ORIGINS: list[str] = []

    # Redis 세션 만료시간 (단위: 초)
    REDIS_SESSION_MAX_AGE: int = Field(
        default=3600,
        description="Redis 세션 유지 시간 (초). 운영 환경에서는 30일로 자동 설정됨"
    )

    # 환경 구분
    ENV: str = Field(
        default="development",
        description="환경 설정 (development, production, test 등)"
    )

    class Config:
        env_file = ".env"  # `.env` 파일에서 환경 변수를 로드
        env_file_encoding = "utf-8"
        extra = "forbid"  # 정의되지 않은 값 에러 발생

    #  프로덕션 여부 판단
    @property
    def IS_PROD(self) -> bool:
        return self.ENV.lower() == "production"

    #  쿠키 보안 관련 자동 설정
    @property
    def COOKIE_SECURE(self) -> bool:
        return self.IS_PROD  # 운영 환경이면 HTTPS 전용 쿠키

    @property
    def COOKIE_HTTPONLY(self) -> bool:
        return True  # 보안상 항상 True

    @property
    def COOKIE_SAMESITE(self) -> str:
        return "Strict" if self.IS_PROD else "Lax"  # 운영은 Strict, 개발은 Lax
    
    # Redis 세션 만료시간 - 운영 환경이면 자동으로 30일로 덮어쓰기
    @property
    def SESSION_MAX_AGE(self) -> int:
        return 60 * 60 * 24 * 30 if self.IS_PROD else self.REDIS_SESSION_MAX_AGE


#  전역적으로 설정을 불러올 수 있도록 인스턴스 생성
settings = Settings()
