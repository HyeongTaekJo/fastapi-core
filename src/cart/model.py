from __future__ import annotations
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from common.model.base_model import Base
from product.model import ProductModel
from typing import List

class CartModel(Base):
    __tablename__ = "cart"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)
    user = relationship("UserModel", backref="cart", lazy="selectin")

    items: Mapped[List[CartItemModel]] = relationship(back_populates="cart", cascade="all, delete-orphan")


class CartItemModel(Base):
    __tablename__ = "cart_item"

    cart_id: Mapped[int] = mapped_column(ForeignKey("cart.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    cart = relationship("CartModel", back_populates="items")
    product = relationship("ProductModel", back_populates="cart_items")
