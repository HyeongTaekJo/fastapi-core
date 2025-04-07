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

    class Config:
        env_file = ".env"  # `.env` 파일에서 환경 변수를 로드
        env_file_encoding = "utf-8"
        extra = "forbid"  # 정의되지 않은 값 에러 발생

# 전역적으로 설정을 불러올 수 있도록 인스턴스 생성
settings = Settings()
