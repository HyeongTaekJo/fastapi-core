from __future__ import annotations
from sqlalchemy import String, Integer, ForeignKey, Enum as SqlEnum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.model.base_model import Base
from typing import Optional
from common.file.file_enum import FileModelType
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from post.model import PostModel

class FileModel(Base):
    __tablename__ = "file"

    path: Mapped[str] = mapped_column(String(255), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[FileModelType] = mapped_column(SqlEnum(FileModelType), nullable=False)

    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_main: Mapped[bool] = mapped_column(default=False, nullable=False)
    # uploaded_at: Mapped[Optional[str]] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # 🔽 범용 연결 (post/user/product 등 다양한 모델에 연결 가능)
    owner_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    owner_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # ✅ (선택) 특정 모델 연결도 추가 (PostModel 관계 사용 시)
    post_id: Mapped[Optional[int]] = mapped_column(ForeignKey("post.id", ondelete="CASCADE"), nullable=True)
    post: Mapped[Optional["PostModel"]] = relationship("PostModel", back_populates="files", lazy="selectin")