from __future__ import annotations
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import String, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from common.model.base_model import Base
from typing import Optional, List, TYPE_CHECKING
import enum

if TYPE_CHECKING:
    from product.model import ProductModel

class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


class OrderModel(Base):
    __tablename__ = "order"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(SqlEnum(OrderStatus), default=OrderStatus.PENDING)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    user = relationship("UserModel", backref="orders", lazy="selectin")
    items: Mapped[List["OrderItemModel"]] = relationship(back_populates="order", cascade="all, delete-orphan", lazy="selectin")


class OrderItemModel(Base):
    __tablename__ = "order_item"

    order_id: Mapped[int] = mapped_column(ForeignKey("order.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_at_time: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["OrderModel"] = relationship("OrderModel", back_populates="items", lazy="selectin")
    product: Mapped["ProductModel"] = relationship("ProductModel", back_populates="order_items", lazy="selectin")
