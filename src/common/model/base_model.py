# from sqlalchemy.orm import declarative_base

# #  모든 모델이 공유할 공통 Base 정의
# Base = declarative_base()
# metadata = Base.metadata  # Alembic과 함께 사용할 메타데이터

from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column


#  모든 모델이 공유할 공통 Base 정의
@as_declarative()
class Base:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    @declared_attr
    def metadata(cls):
        return cls.__table__.metadata