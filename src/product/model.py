from __future__ import annotations
from sqlalchemy import String, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.model.base_model import Base
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from cart.model import CartItemModel
    from order.model import OrderItemModel

class ProductModel(Base):
    __tablename__ = "product"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sku: Mapped[Optional[str]] = mapped_column(String(50), unique=True)

    cart_items: Mapped[List["CartItemModel"]] = relationship(
        "CartItemModel", back_populates="product", cascade="all, delete-orphan"
    )
    order_items: Mapped[List["OrderItemModel"]] = relationship(
        "OrderItemModel", back_populates="product", cascade="all, delete-orphan"
    )
