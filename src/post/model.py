from __future__ import annotations
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from common.model.base_model import Base
from post.schemas.request import CreatePostSchema, UpdatePostSchema
from common.image.model import ImageModel
from typing import List, Optional
from user.model import UserModel


class PostModel(Base):
    __tablename__ = "post"

    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(String(200), nullable=False)
    likeCount: Mapped[int] = mapped_column(default=0, nullable=False)
    commentCount: Mapped[int] = mapped_column(default=0, nullable=False)

    user: Mapped[UserModel] = relationship("UserModel", back_populates="posts", lazy="selectin")
    images: Mapped[List[ImageModel]] = relationship("ImageModel", back_populates="post", cascade="all, delete-orphan", lazy="selectin")

    # pydantic 클래스로 받은 부분을 sqlalchemy.orm으로 변환해주는 작업
    @classmethod
    def create(cls, request: CreatePostSchema) -> "PostModel": # cls는 PostModel 클래스 자체를 의미
        return cls(
            title=request.title,
            content=request.content,
        )
    
    
    @classmethod
    def update(cls, request: UpdatePostSchema) -> "PostModel": # cls는 PostModel 클래스 자체를 의미
        return cls(
            title=request.title,
            content=request.content,
        )
 