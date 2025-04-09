from __future__ import annotations
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from user.const.roles import RolesEnum
from common.model.base_model import Base
from auth.schemas.request import RegisterUserSchema


class UserModel(Base):
    __tablename__ = "user"

    nickname = Column(String(20), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=True) # 로그인 타입 변경시 사용
    login_id = Column(String(50), unique=True)  # 로그인 타입 변경시 사용
    phone = Column(String(20), unique=True) # 로그인 타입 변경시 사용
    password = Column(String(255), nullable=False)  # 해싱된 비밀번호 저장
    role = Column(Enum(RolesEnum), default=RolesEnum.USER)  # 기본값 USER

    # 관계 설정 (문자열 참조로 순환 참조 방지)
    posts = relationship("PostModel", back_populates="user", cascade="all, delete", lazy="selectin")


    # pydantic 클래스로 받은 부분을 sqlalchemy.orm으로 변환해주는 작업
    @classmethod
    def create(cls, request: RegisterUserSchema) -> "UserModel": # cls는 PostModel 클래스 자체를 의미
        return cls(
            nickname=request.nickname,
            email=request.email if request.email else None,
            login_id=request.login_id if request.login_id else None,
            phone=request.phone if request.phone else None,
            password=request.password,
        )