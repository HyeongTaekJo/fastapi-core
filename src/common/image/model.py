from __future__ import annotations
from sqlalchemy import String, Integer, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional, TYPE_CHECKING
from common.model.base_model import Base
from common.image.enums.image_type_enum import ImageModelType


if TYPE_CHECKING:
    from post.model import PostModel

# ImageModel
class ImageModel(Base):
    __tablename__ = "image"

    order: Mapped[int] = mapped_column(default=0, nullable=True)
    type: Mapped[ImageModelType] = mapped_column(SqlEnum(ImageModelType), nullable=False)
    path: Mapped[str] = mapped_column(String(255), nullable=False)
    
    post_id: Mapped[Optional[int]] = mapped_column(ForeignKey("post.id", ondelete="CASCADE"), nullable=True)
    post: Mapped[Optional["PostModel"]] = relationship("PostModel", back_populates="images", lazy="selectin")

