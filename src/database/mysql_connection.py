from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from common.model.base_model import Base
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from fastapi import status
from common.const.settings import settings  # 환경 변수 로드
from sqlalchemy.pool import NullPool  # NullPool 사용

#(환경변수에서 가져오기)
DATABASE_CONN = settings.DATABASE_CONN

# 비동기 엔진 생성
async_engine = create_async_engine(
    DATABASE_CONN,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,
    pool_pre_ping=True,
    # poolclass 생략! 기본값으로 AsyncAdaptedQueuePool 사용
)

# 비동기 세션 팩토리 생성
async_session_maker  = sessionmaker(
    bind=async_engine,
    expire_on_commit=True,  # commit() 후에도 세션이 만료되지 않도록 설정
    autoflush=False,  # 자동 flush 비활성화 (flush()를 직접 호출)
    autocommit=False,  # commit()을 자동으로 수행하지 않음 (수동 처리)
    class_=AsyncSession  # 비동기 세션 사용
)

